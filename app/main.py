from fastapi import FastAPI
from app.core.settings import get_app_settings
from app.controllers.songs import router
from app.db import mongo

settings = get_app_settings()

app = FastAPI(**settings.fastapi_kwargs)
@app.on_event("startup")
async def startup_event():
    songs = mongo.get_database()["songs"]
    await songs.create_index([("title", "text"), ("lyrics", "text")])

app.include_router(router)