import openai
from openai.embeddings_utils import get_embedding
from pymongo import MongoClient
from configsecrets import openai_apikey,mongoConnection

openai.api_key = openai_apikey

def getEmbedding(text):
    # response = openai.Embedding.create(
    #     input=text,
    #     model="text-embedding-ada-002"
    # )
    # embedding_vector = response["data"][0]["embedding"] #type: ignore
    embedding_vector = get_embedding(model="text-embedding-ada-002", prompt=text)
    return embedding_vector


if __name__ == '__main__':
    with MongoClient(mongoConnection['host'], mongoConnection['port'],appName=mongoConnection['appName']) as client:
        client.admin.authenticate(mongoConnection['login'],mongoConnection['password'])
        db = client[mongoConnection["db"]]
        coll = db[mongoConnection["collection"]]
        cursor = coll.find({"embedding": {"$exists": False}})

        for doc in cursor:
            embedding_vector = getEmbedding(doc["text"])
            coll.update_one({'_id': doc['_id']}, {'$set': {'embedding': embedding_vector}})
