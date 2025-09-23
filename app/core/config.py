import os
import json
from functools import lru_cache
from dotenv import load_dotenv

# Load .env file (if exists)
load_dotenv()

class Settings:
    def __init__(self):
        # Core
        self.mongo_uri: str = os.getenv("MONGO_URI")
        self.mongo_db_name: str = os.getenv("MONGO_DB_NAME")
        self.genius_api_url: str = os.getenv("GENIUS_API_URL")
        self.genius_token: str = os.getenv("GENIUS_TOKEN")

    @property
    def fastapi_kwargs(self):
        return {
            "mongo_uri":self.mongo_uri,
            "mongo_db_name":self.mongo_db_name,
            "genius_api_url":self.genius_api_url,
            "genius_token":self.genius_token,
        }


@lru_cache
def get_app_settings() -> Settings:
    return Settings()

