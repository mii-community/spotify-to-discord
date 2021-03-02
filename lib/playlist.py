class Playlist:
    def __init__(self, playlist_data):
        self.name = playlist_data["name"]
        self.url = playlist_data["external_urls"]["spotify"]
        self.image = playlist_data["images"][0]["url"]
        self.items = playlist_data["tracks"]["items"]
        self.total_followers = playlist_data["followers"]["total"]
