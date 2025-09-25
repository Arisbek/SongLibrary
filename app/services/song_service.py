from app.repositories.song_repository import SongRepository
from app.external.genius_client import GeniusClient
from app.external.LRCLib_client import LRCLibProvider
from app.external.spotify_client import SpotifyProvider
from app.models.song import SongCreate, SongReturn
from typing import List, Optional
from fastapi import HTTPException, status
from bson import ObjectId

class SongService:
    """
    Service layer for managing songs.

    Handles business logic between controllers (API layer),
    repositories (database access), and external providers (Genius API).
    """

    def __init__(self, repository: SongRepository, lyrics_provider: GeniusClient, lrclib_provider: LRCLibProvider, spotify_provider=SpotifyProvider, cache=None):
        """
        Initialize the service.

        Args:
            repository (SongRepository): Data access layer for songs.
            lyrics_provider (GeniusClient): External API client for lyrics and metadata.
            cache (Optional[Any]): Optional caching backend (e.g. Redis).
        """
        self.repository = repository
        self.lyrics_provider = lyrics_provider
        self.lrclib_provider = lrclib_provider
        self.spotify_provider = spotify_provider
        self.cache = cache

    async def add_song(self, song_create: dict) -> Optional[dict]:
        """
        Add a new song.

        Workflow:
        - Search song in database. If song is not found proceeds.
        - Look up metadata (release date, link, lyrics) using Genius API.
        - Add metadata with LRCLib if available.
        - Add metadata with Spotify if available.
        - Save enriched song document to MongoDB.
        - Return the saved song with generated ID.

        Args:
            song_create (dict): Dictionary with `title` and `artist`.

        Returns:
            dict: Saved song document with `id`, `title`, `artist`, `release_date`, `link`, `lyrics`.

        Raises:
            HTTPException(409): If the song already exists in the library returns error.
            HTTPException(404): If the song could not be found in Genius API.
            HTTPException(500): If saving to the database fails.
        """
        # 1. Check if already in DB
        existing = await self.repository.search_song(song_create)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Song already exists in library."
            )

        # 2. Fetch from Genius
        external_data = await self.lyrics_provider.search_song(
            song_create["title"], song_create["artist"]
        )
        if not external_data:
            raise HTTPException(
                status_code=404,
                detail=f"Song {song_create['title']} by {song_create['artist']} not found"
            )

        # 3. Build base document
        song_doc = {
            "title": song_create["title"],
            "artist": song_create["artist"],
            "release_date": external_data.get("release_date"),
            "link": external_data.get("link"),
            "lyrics": external_data.get("lyrics")  # Genius fallback
        }

        # 4. Try LRCLib overwrite
        lrclib_data = await self.lrclib_provider.fetch_lyrics(
            song_create["title"], song_create["artist"]
        )
        if lrclib_data:
            # overwrite only if LRCLib returns something valid
            synced = lrclib_data.get("syncedLyrics")
            plain = lrclib_data.get("plainLyrics")

            if synced:
                parsed = synced.split('\n')
                song_doc["lyrics"] = parsed
            elif plain:
                # store plain text line by line as fallback
                song_doc["lyrics"] = plain.split('\n')

        # 5. Try Spotify overwrite (metadata if missing)
        spotify_data = await self.spotify_provider.search_song(
            song_create["title"], song_create["artist"]
        )
        if spotify_data:
            if not song_doc.get("release_date") and spotify_data.get("release_date"):
                song_doc["release_date"] = spotify_data["release_date"]
            if not song_doc.get("link") and spotify_data.get("external_url"):
                song_doc["link"] = spotify_data["external_url"]

            song_doc["spotify_id"] = spotify_data.get("id")

        # 6. Save to Mongo
        song_id = await self.repository.add_song(song_doc)
        if not song_id:
            raise HTTPException(
                status_code=500,
                detail=f"Song cannot be saved in database."
            )
        song_doc["id"] = song_id
        return song_doc

    async def get_song(self, song_id: str, page: int, size: int) -> Optional[dict]:
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
        lyrics = song.get("lyrics", [])
        total = len(lyrics)

        # calculate pagination
        start = (page - 1) * size
        end = start + size
        items = lyrics[start:min(end, total)]
        song["lyrics"] = items
        return song

    async def delete_song(self, song_id: str) -> Optional[str]:
        """
        Delete a song by ID.

        Args:
            song_id (str): MongoDB ObjectId of the song.

        Returns:
            dict: Deleted song document.

        Raises:
            HTTPException(404): If the song does not exist.
        """
        success = await self.repository.delete_song(song_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Song with {song_id=} not found"
            )
        return f"Song with {song_id=} deleted successfully"

    async def update_song(self, song_id: str, data: dict) -> Optional[str]:
        """
        Partially update a song.

        Args:
            song_id (str): MongoDB ObjectId of the song.
            data (dict): Fields to update (title, artist, release_date, etc.).

        Returns:
            msg: outcome of update.

        Raises:
            HTTPException(404): If the song does not exist.
        """
        success = await self.repository.update_song(song_id, data)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Song with {song_id=} not found"
            )
        return f"Song with {song_id=} updated successfully"

    async def search_songs(self, query: dict) -> List[SongReturn]:
        """
        Search for songs.

        Supports filtering by artist, release date, keywords, or link.

        Args:
            query (dict): Search parameters (subset of `SongSearch`).

        Returns:
            List[SongRead]: List of matching songs (possibly empty).
        """
        docs = await self.repository.search_songs(query)
        return [SongReturn(**doc) for doc in docs]
