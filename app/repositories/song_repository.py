from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from bson import ObjectId

class SongRepository:
    def __init__(self, mongo_uri: str, db_name: str):
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db["songs"]

    async def add_song(self, song_data: dict) -> str:
        result = await self.collection.insert_one(song_data)
        print(result)
        return str(result.inserted_id)

    async def get_song(self, song_id: str) -> Optional[dict]:
        try:
            obj_id = ObjectId(song_id)
        except Exception:
            return None

        song = dict(await self.collection.find_one({"_id": obj_id}))
        if song:
            song["id"] = str(song["_id"])
        return song

    async def update_song(self, song_id: str, updates: dict):
        try:
            obj_id = ObjectId(song_id)
        except Exception:
            return None

        # return_document=True gives the updated document
        song = await self.collection.find_one_and_update(
            {"_id": obj_id},
            {"$set": updates},
            return_document=True  # default False, set True for updated doc
        )

        if song:
            song["_id"] = str(song["_id"])
        return song

    async def delete_song(self, song_id: str):
        try:
            obj_id = ObjectId(song_id)
        except Exception:
            return None

        song = await self.collection.find_one_and_delete({"_id": obj_id})
        if song:
            song["_id"] = str(song["_id"])
        return song

    async def search_songs(self, search: dict) -> List[dict]:
        query = {}

        # Filter by release date
        if search.get("release_date", False):
            query["release_date"] = search["release_date"]

        # Filter by link
        if search.get("link", False):
            query["link"] = search["link"]

        # Full-text search by keywords
        if search.get("keywords", False):
            query["$text"] = {"$search": " ".join(search["keywords"])}

        # Perform the query
        cursor = self.collection.find(query)

        # If using text search, sort by relevance
        if "$text" in query:
            cursor = cursor.sort([("score", {"$meta": "textScore"})])
            # cursor = cursor.project({"score": {"$meta": "textScore"}})  # include score in results

        songs = await cursor.to_list(length=100)  # limit to first 100 results
        for song in songs:
            song["id"] = str(song["_id"])
        return songs
