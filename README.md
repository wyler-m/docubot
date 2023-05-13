# Docubot

Create a chatbot that can respond with specific information from any number of documents with help from a large language model (LLM). Much easier than training your own language model. 

It works like this: 

- Spin up the database (default here is MongoDB)
- Insert your document or document fragments into the database. Since a large language model is used to synthesize answers, you need to have a bit of foresight when breaking the docs into fragments. Creating fragments that don't have enough context to be useful in and of themselves tend to be more harmful than helpful
- Once all the documents/document fragments are inserted, retrieve the text embeddings for each one, saving the embedding with the document.
- Make an index of all the embeddings. Indexing and search here uses the [Faiss](https://github.com/facebookresearch/faiss) library. 
- Launch the bot. When a message (we assume its a query) is received by it does the following:
  - Gets a text embedding for the query
  - Use the index of embeddings and the embedding for the query to retrieve documents that are semantically related to the query
  - Concatenate the query, the similar documents, and some instructions into a prompt to send to a large language model. Here we use one of the GPT modesl from OpenAI
  - Log the query and response in the database
  - Return query to the user as a message from the bot.
  - Thumbs Up / Thumbs Down button on the response message allows users to give feedback on the response quality. Responses are recorded as well.



## Setup

Assumes you have:

- Installed Docker in your OS.
- Curated a list of documents or document fragments which you want to make available to chat-GPT (or any other LLM)
- [Created a telegram bot using @botfather](https://core.telegram.org/bots/features#creating-a-new-bot)
- Created an API account with OpenAI or have another way to create text embeddings from text fragments and access an LLM.



1. Create file configsecrets.py with the following secrets:

```
mongoConnection = { "login":"root",
					"password":"root",
					"host":"localhost",
					"port":27017,
					"appName":"<appname>",
					"db":"<db name>",
					"collection":"<db name>" }
telegram_apitoken = "<telegram bot token>"
openai_apikey = "<API key for Openai>"
```
If you're using MongoDB Atlas or another Mongo instance, change connection info as appropriate.

2. Create MongoDB docker instance

```
docker run --name <container_name>  \
-p 27017:27017 \
-v <volumn name>:/data/db \
-e MONGO_INITDB_ROOT_USERNAME=root \
-e MONGO_INITDB_ROOT_PASSWORD=root \
mongo
```

3. Install Python requirements

```
pip install -r requirements.txt
```

3. Add the documents to MongoDB. The main requirement is that each Mongo document should have a field `text`, which contains the text that you want to index, and should not include the field `embedding`. The other requirement is to consider the "size" of the document, that is, the number of tokens. Consider that Chat-GPT 3.5 turbo has a context window of about 4,000 tokens; if the documents are each 2,000 tokens, that means the chatbot will only be able to consider a single document in the prompt. There are models with larger context windows, but ultimately there are cases where you need to split documents into smaller fragments. 

- Once you've added the documents, you can create an archive of the docker volume using something like  `docker exec <container_name> sh -c 'mongodump --authenticationDatabase admin -u root -p root --db <container_name> --archive' > db.dump`

- You can load from an archive using something similar with the mongorestore command: `docker exec -i <container_name> sh -c 'mongorestore --authenticationDatabase admin -u root -p root --db <container_name> --archive' < db.dump`

4. Create embeddings with `python create_embeddings.py`. This can take a while, depending on the number of documents in the database. If something goes wrong, this script can be ran again without problems, since it searches for records without an embedding. **Note: this operation assumes the use of the paid API "embeddings" endpoint from OpenAI**
5. Once embeddings have been added to the documents in the database, run `python build_index.py` to create and save an index based on the embeddings and document IDs. This will allow searches against new embedding vectors.
6. Assuming all the previous steps went correctly, run `python bot.py` and start chatting with your telegram bot! **Note that chatting assumes the use of the paid API "embeddings" and "chat completion" endpoints from OpenAI**

