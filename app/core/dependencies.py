from ..repositories.song_repository import SongRepository
from ..services.song_service import SongService
from ..external.genius_client import GeniusClient
from .config import Settings

def create_dependencies(settings: Settings = None):
    if settings is None:
        from app.core.config import Settings
        settings = Settings()

    repo = SongRepository(mongo_uri=settings.mongo_uri, db_name="songlib")
    genius = GeniusClient()

    song_service = SongService(repository=repo, lyrics_provider=genius)

    return {"song_service": song_service}
