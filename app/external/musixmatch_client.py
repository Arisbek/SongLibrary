import aiohttp
import os


MUSIXMATCH_API_URL = os.getenv("MUSIXMATCH_API_URL", "https://api.musixmatch.com/ws/1.1")
MUSIXMATCH_API_KEY = os.getenv("MUSIXMATCH_API_KEY")


class MusixmatchClient:
    BASE_URL = MUSIXMATCH_API_URL

    def __init__(self):
        if not MUSIXMATCH_API_KEY:
            raise ValueError("MUSIXMATCH_API_KEY is not set in environment variables.")
        self.api_key = MUSIXMATCH_API_KEY

    async def get_lyrics(self, track_id: int):
        """
        Fetch lyrics for a track by Musixmatch track_id.
        """
        params = {
            "apikey": self.api_key,
            "track_id": track_id,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/track.lyrics.get", params=params) as resp:
                data = await resp.json()
                header = data.get("message", {}).get("header", {})
                body = data.get("message", {}).get("body", {})

                if header.get("status_code") == 200 and "lyrics" in body:
                    lyrics = body["lyrics"]["lyrics_body"]
                    return {"track_id": track_id, "lyrics": lyrics}
                else:
                    return {
                        "error": header.get("status_code"),
                        "message": header.get("status_code")
                    }

    async def search_track(self, title: str, artist: str = ""):
        """
        Search for a track by title (and optional artist).
        Returns track_id and basic metadata.
        """
        query = f"{title} {artist}".strip()
        params = {
            "apikey": self.api_key,
            "q_track": title,
        }
        if artist:
            params["q_artist"] = artist

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/track.search", params=params) as resp:
                data = await resp.json()
                header = data.get("message", {}).get("header", {})
                body = data.get("message", {}).get("body", {})

                if header.get("status_code") == 200 and body.get("track_list"):
                    first_track = body["track_list"][0]["track"]
                    return {
                        "track_id": first_track["track_id"],
                        "title": first_track["track_name"],
                        "artist": first_track["artist_name"],
                        "album": first_track.get("album_name"),
                        "explicit": first_track.get("explicit", 0),
                    }
                return None
