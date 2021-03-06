class Playlist:
    def __init__(self, playlist_details):
        self.name = playlist_details["name"]
        self.url = playlist_details["external_urls"]["spotify"]
        self.image = playlist_details["images"][0]["url"]
