from fastapi import FastAPI, HTTPException
from app.core.settings import get_app_settings
from app.controllers.songs import router
from app.db import mongo
from app.core.handlers import http_error_handler
from pymongo import ASCENDING

settings = get_app_settings()

app = FastAPI(**settings.fastapi_kwargs)
@app.on_event("startup")
async def startup_event():
    songs = mongo.get_database()["songs"]
    await songs.create_index([("title", "text"), ("lyrics", "text")])
    await songs.create_index(
        [("title", ASCENDING), ("artist", ASCENDING)],
        unique=True,
        name="unique_title_artist",
    )

app.add_exception_handler(HTTPException, http_error_handler)
app.include_router(router)