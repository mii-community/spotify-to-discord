from datetime import datetime
from os import getenv

from dotenv import load_dotenv
from requests import get

load_dotenv()
PLAYLIST_ID = getenv("PLAYLIST_ID")


class Addition:
    def __init__(self, token, playlist_track):
        self.added_at = playlist_track["added_at"]
        author = get(
            playlist_track["added_by"]["href"],
            headers={"Authorization": f"Bearer {token}"}).json()
        track_detail = get_track_details(token, playlist_track["track"]["id"])
        self.author_name = author["display_name"]
        self.author_url = author["external_urls"]["spotify"]
        self.author_image = author["images"][0]["url"]
        self.track_name = track_detail["name"]
        self.track_url = track_detail["external_urls"][
            "spotify"
        ]
        self.album_image = track_detail["album"]["images"][0]["url"]
        self.artist_name = ", ".join(
            [
                artist["name"]
                for artist in track_detail["artists"]
            ]
        )
        playlist_detail = get_playlist_details(token)
        self.playlist_name = playlist_detail["name"]
        self.playlist_image = playlist_detail["images"][0]["url"]
        self.playlist_url = playlist_detail["external_urls"]["spotify"]


class Deletion:
    def __init__(self, token, playlist_track):
        self.deleted_at = datetime.utcnow().isoformat()
        track_detail = get_track_details(token, playlist_track["track"]["id"])
        self.track_name = track_detail["name"]
        self.track_url = track_detail["external_urls"][
            "spotify"
        ]
        self.album_image = track_detail["album"]["images"][0]["url"]
        self.artist_name = ", ".join(
            [
                artist["name"]
                for artist in track_detail["artists"]
            ]
        )
        playlist_detail = get_playlist_details(token)
        self.playlist_name = playlist_detail["name"]
        self.playlist_image = playlist_detail["images"][0]["url"]
        self.playlist_url = playlist_detail["external_urls"]["spotify"]


def get_playlist_details(token):
    header = {"Authorization": f"Bearer {token}"}
    parmas = {
        "fields": "name,images,external_urls"}
    playlist_detail = get(
        f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}", headers=header, params=parmas).json()
    return playlist_detail


def get_track_details(token, track_id):
    header = {"Authorization": f"Bearer {token}"}
    track_details = get(
        f"https://api.spotify.com/v1/tracks/{track_id}", headers=header).json()
    return track_details
