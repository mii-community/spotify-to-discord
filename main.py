from base64 import b64encode
from os import getenv
from sys import exit
from time import sleep

from dotenv import load_dotenv
from requests import get, post

from lib.addition_or_deletion import Addition

load_dotenv()

CLIENT_ID = getenv("CLIENT_ID")
CLIENT_SECRET = getenv("CLIENT_SECRET")
PLAYLIST_ID = getenv("PLAYLIST_ID")
DISCORD_WEBHOOK_URL = getenv("DISCORD_WEBHOOK_URL")


class SpotifyToDiscord:
    def get_playlist_tracks(self):
        header = {"Authorization": f"Bearer {self.token}"}
        params = {
            "fields": "items(added_at,added_by(href),track(id))",
        }
        tracks = get(
            f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks",
            headers=header,
            params=params,
        ).json()["items"]
        return tracks

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

    def addition_send_to_discord(self, playlist, addition):
        embed = {
            "title": "Added new song!",
            "description": f"__{addition.track_name}__ - {addition.artist_name}",
            "url": addition.track_url,
            "timestamp": addition.added_at,
            "author": {"name": addition.author_name, "url": addition.author_url, "icon_url": addition.author_image},
            "footer": {"text": f"{playlist.name}(Followers: {playlist.total_followers})", "icon_url": playlist.image},
            "thumbnail": {"url": addition.album_image}
        }
        post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})

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
        self.token = post(
            "https://accounts.spotify.com/api/token", headers=header, data=param
        ).json()["access_token"]

    def start(self):
        self.set_new_token()
        self.now_ids = self.make_only_ids(self.get_playlist_tracks())
        while True:
            tracks = self.get_playlist_tracks()
            ids = self.make_only_ids(tracks)
            addition_ids = self.extraction_additions(ids)
            if addition_ids:
                for addition_id in addition_ids:
                    addition_track = self.search_track_from_playlist(
                        tracks, addition_id)
                    self.addition_send_to_discord(
                        self.get_playlist_details(),
                        Addition(self.token, addition_track))
            self.now_ids = ids
            sleep(5)


spotify_to_discord = SpotifyToDiscord()
spotify_to_discord.start()
