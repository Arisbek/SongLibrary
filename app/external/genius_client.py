import aiohttp
import os

GENIUS_API_URL = os.getenv("GENIUS_API_URL")
GENIUS_API_TOKEN = os.getenv("GENIUS_TOKEN")

class GeniusClient:
    BASE_URL = GENIUS_API_URL

    def __init__(self):
        self.token = GENIUS_API_TOKEN
        self.headers = {"Authorization": f"Bearer {self.token}"}

    async def search_song(self, title: str, artist: str):
        query = f"{title} {artist}"
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/search", headers=self.headers, params={"q": query}) as resp:
                data = await resp.json()
                if data["response"]["hits"]:
                    first_hit = data["response"]["hits"][0]["result"]
                    return {
                        "title": first_hit["title"],
                        "artist": first_hit["primary_artist"]["name"],
                        "release_date": first_hit.get("release_date"),
                        "link": first_hit.get("url"),
                        "lyrics": []
                    }
                return None