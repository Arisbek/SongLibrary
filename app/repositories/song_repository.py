from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional

class SongRepository:
    def __init__(self, mongo_uri: str, db_name: str):
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db["songs"]

    async def add_song(self, song_data: dict) -> str:
        result = await self.collection.insert_one(song_data)
        return str(result.inserted_id)

    async def get_song(self, song_id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": song_id})

    async def update_song(self, song_id: str, updates: dict):
        await self.collection.update_one({"_id": song_id}, {"$set": updates})

    async def delete_song(self, song_id: str):
        await self.collection.delete_one({"_id": song_id})

    async def search_songs(self, query: dict) -> List[dict]:
        cursor = self.collection.find(query)
        return [doc async for doc in cursor]
