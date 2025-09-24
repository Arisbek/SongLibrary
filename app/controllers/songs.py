from fastapi import APIRouter, Depends, HTTPException, Body
from ..services.song_service import SongService
from ..models.song import SongCreate, SongRead, SongUpdate, SongSearch
from typing import List, Optional

router = APIRouter()

def get_song_service() -> SongService:
    """
        Dependency injector for SongService.
        Uses core.dependencies.create_dependencies to build the service layer.
    """
    from app.core.dependencies import create_dependencies
    return create_dependencies()["song_service"]

@router.post("/", response_model=SongRead, tags=["Songs"], summary="Add a new song with title and artist", responses={
        404: {"description": "Song not found"},
        500: {"description": "Song cannot be saved in database"},
    },)
async def add_song(song: SongCreate, service: SongService = Depends(get_song_service)):
    """
    Add a new song by title and artist.

    ### Request body
    - **title**: Song title *(string, required)*
    - **artist**: Artist name *(string, required)*

    The service layer will enrich the song with:
    - `release_date`
    - `lyrics`
    - `link` (from Genius API)

    ### Responses
    - **200**: `SongRead` (created song with full details)
    - **404**: Song not found in Genius API
    - **500**: Failed to save the song in the database
    """
    return await service.add_song(dict(song))

@router.get("/{song_id}", response_model=SongRead, tags=["Songs"], summary="Get a song by ID", responses={
        404: {"description": "Song not found"}
    })
async def get_song(song_id: str, service: SongService = Depends(get_song_service)):
    """
    Retrieve a song by its song_id.

    ### Path parameters
    - **song_id**: MongoDB ObjectId of the song *(string, required)*

    ### Responses
    - **200**: `SongRead` (song data)
    - **404**: Song not found
    """
    song = await service.get_song(song_id)
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@router.delete("/{song_id}", tags=["Songs"], summary="Delete a song by ID", responses={
        404: {"description": "Song not found"}
    })
async def delete_song(song_id: str, service: SongService = Depends(get_song_service)):
    """
    Delete a song by its unique identifier.

    ### Path parameters
    - **song_id**: MongoDB ObjectId of the song *(string, required)*

    ### Responses
    - **200**: JSON message confirming deletion
    - **404**: Song not found
    """
    deleted = await service.delete_song(song_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return deleted

@router.patch("/{song_id}", tags=["Songs"], summary="Update a song partially by ID", responses={
        404: {"description": "Song not found"}
    })
async def patch_song(song_id: str, data: SongUpdate = Body(...), service: SongService = Depends(get_song_service)):
    """
    Partially update fields of a song.

    ### Path parameters
    - **song_id**: MongoDB ObjectId *(string, required)*

    ### Request body
    Any subset of:
    - **title** *(string, optional)*
    - **artist** *(string, optional)*
    - **release_date** *(string, optional, ISO format)*

    ### Responses
    - **200**: Updated `SongRead`
    - **404**: Song not found
    """
    updated = await service.update_song(song_id, data.dict(exclude_unset=True))
    if updated is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return updated

@router.post("/search", response_model=List[SongRead], tags=["Songs"], summary="Search songs by artist, keywords or release date range")
async def search_songs(
    search: SongSearch = Body(...),
    service: "SongService" = Depends(get_song_service)
):
    """
    Search for songs using flexible filters.

    ### Request body
    - **keywords** *(string, optional)*: Text to match in title, artist, or lyrics
    - **release_date** *(string, optional, ISO format)*: Exact release date
    - **link** *(string, optional)*: Source link

    ### Responses
    - **200**: List of `SongRead` matching search criteria (possibly empty)
    """
    results = await service.search_songs(search.dict(exclude_unset=True))
    return results
