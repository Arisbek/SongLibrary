from app.repositories.song_repository import SongRepository
from app.external.genius_client import GeniusClient
from app.models.song import SongCreate, SongRead, LyricsVerse
from typing import List, Optional
from fastapi import HTTPException, status
from bson import ObjectId

class SongService:
    """
    Service layer for managing songs.

    Handles business logic between controllers (API layer),
    repositories (database access), and external providers (Genius API).
    """

    def __init__(self, repository: SongRepository, lyrics_provider: GeniusClient, cache=None):
        """
        Initialize the service.

        Args:
            repository (SongRepository): Data access layer for songs.
            lyrics_provider (GeniusClient): External API client for lyrics and metadata.
            cache (Optional[Any]): Optional caching backend (e.g. Redis).
        """
        self.repository = repository
        self.lyrics_provider = lyrics_provider
        self.cache = cache

    async def add_song(self, song_create: dict) -> Optional[dict]:
        """
        Add a new song.

        Workflow:
        - Look up metadata (release date, link, lyrics) using Genius API.
        - Save enriched song document to MongoDB.
        - Return the saved song with generated ID.

        Args:
            song_create (dict): Dictionary with `title` and `artist`.

        Returns:
            dict: Saved song document with `id`, `title`, `artist`, `release_date`, `link`, `lyrics`.

        Raises:
            HTTPException(404): If the song could not be found in Genius API.
            HTTPException(500): If saving to the database fails.
        """
        # Enrich song via external API
        external_data = await self.lyrics_provider.search_song(song_create["title"], song_create["artist"])
        if not external_data:
            raise HTTPException(
                status_code=404,
                detail=f"Song with {song_create['title']=} and {song_create['artist']=} not found"
            )

        song_doc = {
            "title": song_create["title"],
            "artist": song_create["artist"],
            "release_date": external_data.get("release_date"),
            "link": external_data.get("link"),
            "lyrics": external_data.get("lyrics")  # list of dicts: [{"index": 0, "text": "verse"}]
        }

        song_id = await self.repository.add_song(song_doc)
        if not song_id:
            raise HTTPException(
                status_code=500,
                detail=f"Song cannot be saved in database."
            )
        song_doc["id"] = song_id
        return song_doc

    async def get_song(self, song_id: str) -> Optional[dict]:
        """
        Retrieve a song by ID.

        Args:
            song_id (str): MongoDB ObjectId of the song.

        Returns:
            dict: Song document with metadata and lyrics.

        Raises:
            HTTPException(404): If no song is found with the given ID.
        """
        song = await self.repository.get_song(song_id)
        if not song:
            raise HTTPException(
                status_code=404,
                detail=f"Song with {song_id=} not found"
            )
        return song

    async def delete_song(self, song_id: str) -> Optional[dict]:
        """
        Delete a song by ID.

        Args:
            song_id (str): MongoDB ObjectId of the song.

        Returns:
            dict: Deleted song document.

        Raises:
            HTTPException(404): If the song does not exist.
        """
        deleted_song = await self.repository.delete_song(song_id)
        if not deleted_song:
            raise HTTPException(
                status_code=404,
                detail=f"Song with {song_id=} not found"
            )
        return deleted_song

    async def update_song(self, song_id: str, data: dict) -> Optional[dict]:
        """
        Partially update a song.

        Args:
            song_id (str): MongoDB ObjectId of the song.
            data (dict): Fields to update (title, artist, release_date, etc.).

        Returns:
            dict: Updated song document.

        Raises:
            HTTPException(404): If the song does not exist.
        """
        updated_song = await self.repository.update_song(song_id, data)
        if not updated_song:
            raise HTTPException(
                status_code=404,
                detail=f"Song with {song_id=} not found"
            )
        return updated_song

    async def search_songs(self, query: dict) -> List[SongRead]:
        """
        Search for songs.

        Supports filtering by artist, release date, keywords, or link.

        Args:
            query (dict): Search parameters (subset of `SongSearch`).

        Returns:
            List[SongRead]: List of matching songs (possibly empty).
        """
        docs = await self.repository.search_songs(query)
        return [SongRead(**doc) for doc in docs]
