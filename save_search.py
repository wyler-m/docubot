from pymongo import MongoClient
import bson
from configsecrets import mongoConnection

def save_query(query_text,chat_id,user_id,query_result,processed_query=""):
    with MongoClient(mongoConnection['host'], mongoConnection['port'],appName=mongoConnection['appName']) as client:
        client.admin.authenticate(mongoConnection['login'],mongoConnection['password'])
        db = client[mongoConnection["db"]]
        coll = db["searches"]
        response = coll.insert_one({
            "query":query_text,
            "result":query_result,
            "chat_id":chat_id,
            "user_id":user_id,
            "processed_query":processed_query
        })
    return str(response.inserted_id)

def rate_query(object_id,rating):
    with MongoClient(mongoConnection['host'], mongoConnection['port'],appName=mongoConnection['appName']) as client:
        client.admin.authenticate(mongoConnection['login'],mongoConnection['password'])
        db = client[mongoConnection["db"]]
        coll = db["searches"]
        coll.update_one({"_id":bson.ObjectId(object_id)},{"$set":{"eval":rating}})
    