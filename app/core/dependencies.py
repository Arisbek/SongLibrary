from ..repositories.song_repository import SongRepository
from ..services.song_service import SongService
from ..external.genius_client import GeniusClient
from ..external.LRCLib_client import LRCLibProvider
from ..external.spotify_client import SpotifyProvider
from .config import Settings

def create_dependencies(settings: Settings = None):
    if settings is None:
        from app.core.config import Settings
        settings = Settings()

    repo = SongRepository(mongo_uri=settings.mongo_uri, db_name=settings.mongo_db_name)
    genius = GeniusClient()
    lrclib_provider = LRCLibProvider()
    spotify_provider = SpotifyProvider()

    song_service = SongService(repository=repo, lyrics_provider=genius, lrclib_provider=lrclib_provider, spotify_provider=spotify_provider)

    return {"song_service": song_service}
