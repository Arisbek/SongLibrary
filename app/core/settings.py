import os
import json
from functools import lru_cache
from dotenv import load_dotenv

# Load .env file (if exists)
load_dotenv()

class Settings:
    def __init__(self):
        # Core
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.docs_url: str = os.getenv("DOCS_URL", "/docs")
        self.redoc_url: str = os.getenv("REDOC_URL", "/redoc")
        self.title: str = os.getenv("TITLE", "FastAPI App")
        self.description: str = os.getenv("DESCRIPTION", "API Description")

        # API
        self.api_prefix: str = "/api"
        self.allowed_hosts = self._parse_hosts(os.getenv("ALLOWED_HOSTS", "*"))

    @staticmethod
    def _parse_hosts(value: str):
        # Try JSON first
        try:
            return json.loads(value)
        except Exception:
            return [h.strip() for h in value.split(",") if h.strip()]

    @property
    def fastapi_kwargs(self):
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "description": self.description,
        }


@lru_cache
def get_app_settings() -> Settings:
    return Settings()

