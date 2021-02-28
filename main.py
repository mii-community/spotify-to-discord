from base64 import b64encode
from os import getenv
from time import sleep

from dotenv import load_dotenv
from requests import get, post

load_dotenv()

CLIENT_ID = getenv("CLIENT_ID")
CLIENT_SECRET = getenv("CLIENT_SECRET")
PLAYLIST_ID = getenv("PLAYLIST_ID")
DISCORD_WEBHOOK_URL = getenv("DISCORD_WEBHOOK_URL")


class SpotifyToDiscord:
    def get_playlist_items(self):
        header = {"Authorization": f"Bearer {self.token}"}
        params = {
            "market": "JP",
            "fields": "tracks.items(added_by(href),track(name,external_urls,artists(name),id))",
        }
        items = get(
            f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}",
            headers=header,
            params=params,
        )
        return items

    def get_user_name(self, href):
        header = {"Authorization": f"Bearer {self.token}"}
        user_name = get(href, headers=header).json()["display_name"]
        return user_name

    def set_new_token(self):
        encoded_code = b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        header = {"Authorization": f"Basic {encoded_code}"}
        param = {"grant_type": "client_credentials"}
        self.token = post(
            "https://accounts.spotify.com/api/token", headers=header, data=param
        ).json()["access_token"]

    def extraction_additions(self, items):
        additions = []
        for item in items:
            if item not in self.now_items:
                additions.append(item)
        return additions

    def combine_additions(self, additions):
        for addition in additions:
            track_name = addition["track"]["name"]
            track_spotify_url = addition["track"]["external_urls"]["spotify"]
            track_artist_name = " & ".join(
                [artist["name"] for artist in addition["track"]["artists"]]
            )
            added_user_name = self.get_user_name(addition["added_by"]["href"])
            yield (track_name, track_artist_name, track_spotify_url, added_user_name)

    def extraction_deletions(self, items):
        deletions = []
        for now_item in self.now_items:
            if now_item not in items:
                deletions.append(now_item)
        return deletions

    @staticmethod
    def error_handling(exception):
        post(DISCORD_WEBHOOK_URL, json={"content": f"内部エラーが発生しました:{exception}"})

    def start(self):
        self.set_new_token()
        self.now_items = self.get_playlist_items().json()["tracks"]["items"]
        while True:
            items = self.get_playlist_items().json()["tracks"]["items"]
            additions = self.extraction_additions(items)
            if additions:
                for combined_addition in self.combine_additions(additions):
                    print(combined_addition)
            deletions = self.extraction_deletions(items)
            if deletions:
                print(deletions)
            self.now_items = items
            sleep(1)


spotify_to_discord = SpotifyToDiscord()
spotify_to_discord.start()
