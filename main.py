from base64 import b64encode
from os import getenv
from sys import exit
from time import sleep

from dotenv import load_dotenv
from requests import get, post

from lib.addition_or_deletion import AddtionOrDeletion
from lib.playlist import Playlist

load_dotenv()

CLIENT_ID = getenv("CLIENT_ID")
CLIENT_SECRET = getenv("CLIENT_SECRET")
PLAYLIST_ID = getenv("PLAYLIST_ID")
DISCORD_WEBHOOK_URL = getenv("DISCORD_WEBHOOK_URL")


class SpotifyToDiscord:
    def get_playlist(self):
        header = {"Authorization": f"Bearer {self.token}"}
        params = {
            "market": "JP",
            "fields": "name,external_urls,followers,images,tracks.items(added_at,added_by(href),track(name,external_urls,album(images),artists(name)))",
        }
        playlist = get(
            f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}",
            headers=header,
            params=params,
        )
        return playlist

    def set_new_token(self):
        encoded_code = b64encode(
            f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        header = {"Authorization": f"Basic {encoded_code}"}
        param = {"grant_type": "client_credentials"}
        self.token = post(
            "https://accounts.spotify.com/api/token", headers=header, data=param
        ).json()["access_token"]

    def extraction_additions(self, items):
        additions = list(filter(lambda x: x not in self.now_items, items))
        return additions

    def extraction_deletions(self, items):
        deletions = []
        for now_item in self.now_items:
            if now_item not in items:
                deletions.append(now_item)
        return deletions

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
        print(addition.album_image)
        post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})

    @staticmethod
    def error_handling(exception_text):
        post(
            DISCORD_WEBHOOK_URL, json={
                "content": f"内部エラーが発生しました。\n```{exception_text}```\nシステムを終了します。"}
        )
        exit()

    def start(self):
        self.set_new_token()
        self.now_items = self.get_playlist().json()["tracks"]["items"]
        while True:
            playlist = Playlist(self.get_playlist().json())
            print(playlist.items)
            additions = self.extraction_additions(playlist.items)
            if additions:
                for addition in additions:
                    self.addition_send_to_discord(
                        playlist, AddtionOrDeletion(self.token, addition))
            deletions = self.extraction_deletions(playlist.items)
            if deletions:
                for combined_deletion in self.combine_additions_or_deletions(deletions):
                    print(combined_deletion)
            self.now_items = playlist.items
            sleep(5)


spotify_to_discord = SpotifyToDiscord()
spotify_to_discord.start()
