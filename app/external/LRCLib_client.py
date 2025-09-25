import aiohttp
import os

class LRCLibProvider:
    BASE_URL = os.getenv("LRCLIB_URL")

    async def fetch_lyrics(self, title: str, artist: str) -> dict | None:
        params = {"track_name": title, "artist_name": artist}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, params=params) as resp:
                    if resp.status != 200:
                        return None
                    return await resp.json()
        except Exception as e:
            print(f"LRCLib API error: {e}")
            return None
