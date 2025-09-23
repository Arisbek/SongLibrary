from motor.motor_asyncio import AsyncIOMotorClient
import os

def get_mongo_client():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    return AsyncIOMotorClient(mongo_uri)

def get_database():
    client = get_mongo_client()
    db_name = os.getenv("MONGO_DB_NAME", "songlib")
    return client[db_name]
