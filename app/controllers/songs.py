from fastapi import APIRouter, Depends, HTTPException
from ..services.song_service import SongService
from ..models.song import SongCreate, SongRead
from typing import List, Optional

router = APIRouter()

# Dependency injection
def get_song_service() -> SongService:
    from app.core.dependencies import create_dependencies
    return create_dependencies()["song_service"]

@router.post("/", response_model=SongRead, tags=["Songs"], summary="Add a new song")
async def add_song(song: SongCreate, service: SongService = Depends(get_song_service)):
    """Add a new song by title and artist. Enriches song with release date, lyrics, and link from Genius API."""
    return await service.add_song(song)

@router.get("/{song_id}", response_model=SongRead, tags=["Songs"], summary="Get a song by ID")
async def get_song(song_id: str, service: SongService = Depends(get_song_service)):
    """Retrieve a song by its ID."""
    song = await service.get_song(song_id)
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@router.get(
    "/",
    response_model=List[SongRead],
    tags=["Songs"],
    summary="Search songs",
)
async def search_songs(
    title: Optional[str] = None,
    artist: Optional[str] = None,
    service: SongService = Depends(get_song_service),
):
    """Search songs by title and/or artist."""
    return await service.search_songs(title=title, artist=artist)
