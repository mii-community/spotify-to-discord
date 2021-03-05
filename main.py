from base64 import b64encode
from os import getenv
from sys import exit
from time import sleep

from dotenv import load_dotenv
from requests import get, post
from requests.exceptions import RequestException

from lib.addition_or_deletion import Addition, Deletion

load_dotenv()

CLIENT_ID = getenv("CLIENT_ID")
CLIENT_SECRET = getenv("CLIENT_SECRET")
PLAYLIST_ID = getenv("PLAYLIST_ID")
DISCORD_WEBHOOK_URL = getenv("DISCORD_WEBHOOK_URL")


class SpotifyToDiscord:
    def get_playlist_tracks(self):
        header = {"Authorization": f"Bearer {self.token}"}
        next_url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"
        params = {
            "fields": "next,items(added_at,added_by(href),track(id))",
            "market": "JP"
        }
        all_tracks = []
        while True:
            try:
                response = get(
                    next_url,
                    headers=header,
                    params=params
                )
                response.raise_for_status()
                all_tracks.extend(response.json()["items"])
            except RequestException as e:
                self.error_handling(e)
            if (next_url := response.json()["next"]) is None:
                return all_tracks

    def make_only_ids(self, tracks):
        ids = [track["track"]["id"] for track in tracks]
        return set(ids)

    def search_track_from_playlist(self, tracks, id):
        for track in tracks:
            if track["track"]["id"] == id:
                return track

    def extraction_additions(self, ids):
        additions = ids - self.now_ids
        return additions

    def extraction_deletions(self, ids):
        deletions = self.now_ids - ids
        return deletions

    def addition_send_to_discord(self, addition):
        embed = {
            "title": "Added new song!",
            "description": f"__{addition.track_name}__ - {addition.artist_name}",
            "url": addition.track_url,
            "timestamp": addition.added_at,
            "author": {"name": addition.author_name, "url": addition.author_url, "icon_url": addition.author_image},
            "footer": {"text": f"{addition.playlist_name}", "icon_url": addition.playlist_image},
            "thumbnail": {"url": addition.album_image}
        }
        try:
            response = post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})
            response.raise_for_status()
        except RequestException as e:
            self.error_handling(e)
        return

    def deletion_send_to_discord(self, deletion):
        embed = {
            "title": "Removed the song",
            "description": f"__{deletion.track_name}__ - {deletion.artist_name}",
            "url": deletion.track_url,
            "timestamp": deletion.deleted_at,
            "footer": {"text": f"{deletion.playlist_name}", "icon_url": deletion.playlist_image},
            "thumbnail": {"url": deletion.album_image}
        }
        try:
            response = post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})
            response.raise_for_status()
        except RequestException as e:
            self.error_handling(e)
        return

    @staticmethod
    def error_handling(exception_text):
        post(
            DISCORD_WEBHOOK_URL, json={
                "content": f"内部エラーが発生しました。\n```{exception_text}```\nシステムを終了します。"}
        )
        exit()

    def set_new_token(self):
        encoded_code = b64encode(
            f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        header = {"Authorization": f"Basic {encoded_code}"}
        param = {"grant_type": "client_credentials"}
        try:
            response = post(
                "https://accounts.spotify.com/api/token", headers=header, data=param
            )
            response.raise_for_status()
        except RequestException as e:
            self.error_handling(e)
        self.token = response.json()["access_token"]

    def start(self):
        self.set_new_token()
        self.now_tracks = self.get_playlist_tracks()
        self.now_ids = self.make_only_ids(self.now_tracks)
        while True:
            tracks = self.get_playlist_tracks()
            ids = self.make_only_ids(tracks)
            addition_ids = self.extraction_additions(ids)
            if addition_ids:
                for addition_id in addition_ids:
                    addition_track = self.search_track_from_playlist(
                        tracks, addition_id)
                    self.addition_send_to_discord(
                        Addition(self.token, addition_track))
            deletion_ids = self.extraction_deletions(ids)
            if deletion_ids:
                for deletion_id in deletion_ids:
                    deletion_track = self.search_track_from_playlist(
                        self.now_tracks, deletion_id)
                    self.deletion_send_to_discord(
                        Deletion(self.token, deletion_track))
            self.now_tracks = tracks
            self.now_ids = ids
            sleep(5)


spotify_to_discord = SpotifyToDiscord()
spotify_to_discord.start()
