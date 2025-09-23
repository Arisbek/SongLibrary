# app/models/song.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from .lyrics_verse import LyricsVerse

class SongBase(BaseModel):
    title: str = Field(..., description="Title of the song")
    artist: str = Field(..., description="Name of the artist")
    artist: str = Field(..., description="Name of the artist")

class SongCreate(SongBase):
    pass  # additional fields if needed

class SongRead(SongBase):
    id: str = Field(..., description="Unique ID of the song in the database")
    release_date: Optional[date] = Field(None, description="Release date of the song")
    lyrics: Optional[List[LyricsVerse]] = Field(None, description="List of lyrics verses")
    link: Optional[str] = Field(None, description="Link to the song in external API")
