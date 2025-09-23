from fastapi import APIRouter, Depends, HTTPException, Body
from ..services.song_service import SongService
from ..models.song import SongCreate, SongRead, SongUpdate, SongSearch
from typing import List, Optional

router = APIRouter()

def get_song_service() -> SongService:
    from app.core.dependencies import create_dependencies
    return create_dependencies()["song_service"]

@router.post("/", response_model=SongRead, tags=["Songs"], summary="Add a new song")
async def add_song(song: SongCreate, service: SongService = Depends(get_song_service)):
    """Add a new song by title and artist. Enriches song with release date, lyrics, and link from Genius API."""
    return await service.add_song(dict(song))

@router.get("/{song_id}", response_model=SongRead, tags=["Songs"], summary="Get a song by ID")
async def get_song(song_id: str, service: SongService = Depends(get_song_service)):
    """Retrieve a song by its ID."""
    song = await service.get_song(song_id)
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@router.delete("/{song_id}", tags=["Songs"], summary="Delete a song by ID")
async def delete_song(song_id: str, service: SongService = Depends(get_song_service)):
    """Delete a song by its ID."""
    deleted = await service.delete_song(song_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return deleted

@router.patch("/{song_id}", tags=["Songs"], summary="Update a song partially by ID")
async def patch_song(song_id: str, data: SongUpdate = Body(...), service: SongService = Depends(get_song_service)):
    """Update a song partially."""
    updated = await service.update_song(song_id, data.dict(exclude_unset=True))
    if updated is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return updated

@router.post("/search", response_model=List[SongRead], tags=["Songs"], summary="Search songs by keywords or release date")
async def search_songs(
    search: SongSearch = Body(...),
    service: "SongService" = Depends(get_song_service)
):
    """
    Search for songs by keywords, release date, or link.
    """
    results = await service.search_songs(search.dict(exclude_unset=True))
    return results
