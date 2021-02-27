from base64 import b64encode
from os import getenv

from dotenv import load_dotenv
from requests import get, post

load_dotenv()

CLIENT_ID = getenv("CLIENT_ID")
CLIENT_SECRET = getenv("CLIENT_ID")
PLAYLIST_ID = getenv("PLAYLIST_ID")


class SpotifyToDiscord:
    def get_playlist_items(self):
        header = {"Authorization": f"Bearer {self.token}"}
        query_param = {"fields": "items(added_by(href),track(name,artists(name))"}
        result = get(
            f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks",
            headers=header,
            params=query_param,
        )
        return result.json()

    def make_token(self):
        encoded_code = b64encode(
            f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
        ).decode()
        header = {"Authorization": f"Basic {encoded_code}"}
        param = {"grant_type": "client_credentials"}
        self.token = post(
            "https://accounts.spotify.com/api/token", headers=header, data=param
        ).json()["access_token"]
