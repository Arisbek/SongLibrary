import aiohttp
import asyncio
import base64
import os
from typing import Optional, Dict


class SpotifyProvider:
    """
    Wrapper for Spotify Web API search endpoints.

    - Authenticates with Client Credentials flow
    - Searches for a track by title + artist
    - Returns metadata (release_date, external_url, cover_art, id)
    """

    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.token_url = os.getenv("SPOTIFY_TOKEN_URL")
        self.search_url = os.getenv("SPOTIFY_URL")
        self.access_token: Optional[str] = None

    async def _get_access_token(self) -> str:
        if self.access_token:
            return self.access_token

        if not self.client_id or not self.client_secret:
            raise Exception("Spotify CLIENT_ID or CLIENT_SECRET not set")

        # Basic auth: base64(client_id:client_secret)
        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()

        headers = {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}

        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=data, headers=headers) as resp:
                text = await resp.text()
                if resp.status != 200:
                    raise Exception(f"Spotify token error: {resp.status}, body={text}")

                token_data = await resp.json()
                self.access_token = token_data["access_token"]
                return self.access_token

    async def search_song(self, title: str, artist: str) -> Optional[Dict]:
        """
        Search for a track by title + artist.
        Returns first match metadata or None.
        """
        token = await self._get_access_token()
        query = f"track:{title} artist:{artist}"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.search_url,
                params={"q": query, "type": "track", "limit": 1},
                headers={"Authorization": f"Bearer {token}"},
            ) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                items = data.get("tracks", {}).get("items", [])
                if not items:
                    return None

                track = items[0]
                return {
                    "id": track["id"],
                    "release_date": track["album"]["release_date"],
                    "external_url": track["external_urls"]["spotify"],
                    "cover_art": track["album"]["images"][0]["url"]
                    if track["album"]["images"]
                    else None,
                }
