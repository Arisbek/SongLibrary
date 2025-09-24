from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from .lyrics_verse import LyricsVerse

class SongBase(BaseModel):
    title: str = Field(..., description="Title of the song")
    artist: str = Field(..., description="Name of the artist")

class SongCreate(SongBase):
    pass  # additional fields if needed

class SongRead(SongBase):
    id: str = Field(..., description="Unique ID of the song in the database")
    release_date: Optional[date] = Field(None, description="Release date of the song")
    lyrics: Optional[List[LyricsVerse]] = Field(None, description="List of lyrics verses")
    link: Optional[str] = Field(None, description="Link to the song in external API")

class SongSearch(BaseModel):
    release_date_from: Optional[date] = None
    release_date_to: Optional[date] = None
    keywords: Optional[List[str]] = None
    link: Optional[str] = None
    class Config:
        schema_extra = {
            "example": {
                "keywords": ["string"]
            }
        }

class SongUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    lyrics: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "title": "New Song Title"
            }
        }