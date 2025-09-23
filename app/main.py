from fastapi import FastAPI
from app.core.settings import get_app_settings
from app.controllers.songs import router

settings = get_app_settings()

app = FastAPI(**settings.fastapi_kwargs)

app.include_router(router)