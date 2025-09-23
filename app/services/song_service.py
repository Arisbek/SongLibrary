from app.repositories.song_repository import SongRepository
from app.external.genius_client import GeniusClient
from app.models.song import SongCreate, SongRead, LyricsVerse
from typing import List, Optional
from fastapi import HTTPException, status
from bson import ObjectId

class SongService:
    def __init__(self, repository: SongRepository, lyrics_provider: GeniusClient, cache=None):
        self.repository = repository
        self.lyrics_provider = lyrics_provider
        self.cache = cache

    async def add_song(self, song_create: dict) -> SongRead:
        # Enrich song via external API
        external_data = await self.lyrics_provider.search_song(song_create["title"], song_create["artist"])
        if external_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Song %'{song_create['title']}' by %'{song_create['artist']}' not found."
            )

        song_doc = {
            "title": song_create["title"],
            "artist": song_create["artist"],
            "release_date": external_data.get("release_date"),
            "link": external_data.get("link"),
            "lyrics": external_data.get("lyrics")  # list of dicts: [{"index": 0, "text": "verse"}]
        }

        song_id = await self.repository.add_song(song_doc)
        return SongRead(id=song_id, **song_doc)

    async def get_song(self, song_id: str) -> SongRead:
        doc = await self.repository.get_song(song_id)
        if doc is None:
            return None
        return SongRead(**doc)

    async def delete_song(self, song_id: str) -> Optional[dict]:
        """Delete song by id"""
        deleted_song = await self.repository.delete_song(song_id)
        if deleted_song:
            deleted_song["_id"] = str(deleted_song["_id"])
        return deleted_song

    async def update_song(self, song_id: str, data: dict) -> Optional[dict]:
        """Partial update of song fields."""
        updated_song = await self.repository.update_song(song_id, data)
        if updated_song:
            updated_song["_id"] = str(updated_song["_id"])
        return updated_song

    async def search_songs(self, query: dict) -> List[SongRead]:
        docs = await self.repository.search_songs(query)
        return [SongRead(**doc) for doc in docs]
