from telegram import Update, InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import logging
from build_chat import respond_to_query
from save_search import save_query, rate_query
import json
from configsecrets import telegram_apitoken

WELCOME_MESSAGE = "Welcome to the chatter. Please enter a query to get started."
ERROR_MESSAGE = "Oh No! Something went wrong with the request. The error has been logged. Please try again or contact the administrator.  

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def callback_keyboard(search_id,response=""):
    keyboard = []
    options = [
        ("👍",json.dumps({"search_id":search_id,"eval":1})),
        ("👎",json.dumps({"search_id":search_id,"eval":0}))
    ]
    if response == "good":
        options = [
            ("Selected[👍]",json.dumps({"search_id":search_id,"eval":1})),
            ("👎",json.dumps({"search_id":search_id,"eval":0}))
        ]
    elif response == "bad":
        options = [
            ("👍",json.dumps({"search_id":search_id,"eval":1})),
            ("Selected[👎]",json.dumps({"search_id":search_id,"eval":0}))
        ]    
    for option in options:
        keyboard.append([InlineKeyboardButton(option[0], callback_data=option[1])])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}.\n{WELCOME_MESSAGE}') 

async def query_on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_id = update.message.message_id
    chat_id = update.message.chat_id
    user_id = update.effective_user.name
    query = str(update.message.text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Processing your request",reply_to_message_id=message_id)
    try:
        response, processed_query = respond_to_query(query)
    except Exception:
        response = ERROR_MESSAGE
        inserted_id = save_query(query,chat_id,user_id,"ERROR")
    try:
        inserted_id = save_query(query,chat_id,user_id,response,processed_query)
        keyboard_markup = callback_keyboard(inserted_id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response,reply_markup=keyboard_markup,reply_to_message_id=message_id)
    except Exception:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, no response could be provided, please try again")


async def process_callback_keyboard(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = json.loads(query.data)
    rate_query(callback_data["search_id"],callback_data["eval"])
    if callback_data["eval"] == 1:
        keyboard_markup = callback_keyboard(callback_data["search_id"],"good")
    else:
        keyboard_markup = callback_keyboard(callback_data["search_id"],"bad")
    await query.edit_message_reply_markup(keyboard_markup)
    

app = ApplicationBuilder().token(telegram_apitoken).build()
echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), query_on_message)
app.add_handler(echo_handler)
app.add_handler(CommandHandler("start", hello))
app.add_handler(CallbackQueryHandler(process_callback_keyboard))
app.run_polling()
