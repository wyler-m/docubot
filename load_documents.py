from pymongo import MongoClient
import tiktoken
from configsecrets import mongoConnection

def upload_to_mongo(data):
    # connect to mongodb
    with MongoClient(host=mongoConnection["host"], 
                     port=mongoConnection["port"], 
                     username=mongoConnection["login"], 
                     password=mongoConnection["password"]
                     ) as client:
        db = client["db"]
        collection = db["cloudblue"]
        # insert data
        collection.insert_one(data)

def count_tokens(text:str)->int:
    encoding = tiktoken.encoding_for_model("text-embedding-ada-002")
    return len(encoding.encode(text))

def get_text_info(document) -> dict:
    # do something to get info from the document
    return {"text":text, "title":title, "author":author, "url":url, "token_count":count_tokens(text)}

def split_text(text:str, MAX_TOKENS) -> list:
    # split text into chunks that are smaller than the max token count, if needed
    return text_chunks


if __name__ == "__main__":
    
    MAX_TOKENS = 512

    documents = ["**some","list", "of", "documents**"]

    for document in documents:
        text_info = get_text_info(document)
        # check if the text is too long, in which case, break into chunks as needed
        if text_info["token_count"] > MAX_TOKENS:
            text_chunks = split_text(text_info["text"],MAX_TOKENS)
            for chunk in text_chunks:
                token_count = count_tokens(chunk)
                text_info["token_count"] = token_count
                text_info["text"] = chunk
                upload_to_mongo(text_info)
        else:
            upload_to_mongo(text_info)
