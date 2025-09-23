# app/models/lyrics_verse.py
from pydantic import BaseModel, Field

class LyricsVerse(BaseModel):
    index: int = Field(..., description="Verse number in the song")
    text: str = Field(..., description="Text of the verse")