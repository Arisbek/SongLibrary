import aiohttp
import os


GENIUS_API_URL = os.getenv("GENIUS_API_URL")
GENIUS_API_TOKEN = os.getenv("GENIUS_TOKEN")


class GeniusClient:
    BASE_URL = GENIUS_API_URL

    def __init__(self):
        if not GENIUS_API_TOKEN:
            raise ValueError("GENIUS_TOKEN is not set in environment variables.")
        self.token = GENIUS_API_TOKEN
        self.headers = {"Authorization": f"Bearer {self.token}"}

    async def search_song(self, title: str, artist: str):
        """
        Search Genius API and return exact match for title + artist.
        Case-insensitive, ignores small punctuation differences.
        """
        query = f"{title} {artist}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/search",
                headers=self.headers,
                params={"q": query},
            ) as resp:
                data = await resp.json()
                hits = data.get("response", {}).get("hits", [])

                if not hits:
                    return None

                # Normalize strings for comparison
                def normalize(s: str) -> str:
                    return "".join(ch.lower() for ch in s if ch.isalnum())

                norm_title = normalize(title)
                norm_artist = normalize(artist)

                for hit in hits:
                    result = hit["result"]
                    hit_title = normalize(result["title"])
                    hit_artist = normalize(result["primary_artist"]["name"])

                    if hit_title == norm_title and hit_artist == norm_artist:
                        return {
                            "title": result["title"],
                            "artist": result["primary_artist"]["name"],
                            "release_date": result.get("release_date"),
                            "link": result.get("url"),
                            "lyrics": [],  # You’d still fetch separately
                        }

                # No exact match found
                return None
