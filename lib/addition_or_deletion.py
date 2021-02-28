from requests import get


class AddtionOrDeletion:
    def __init__(self, item_data, token):
        self.added_at = item_data["added_at"]
        author = get(
            item_data["added_by"]["href"],
            headers={"Authorization": f"Bearer {token}"}).json()
        self.author_name = author["display_name"]
        self.author_url = author["external_urls"]["spotify"]
        self.author_image = author["images"][0]["url"]
        self.track_name = item_data["track"]["name"]
        self.track_url = item_data["track"]["external_urls"][
            "spotify"
        ]
        self.artist_name = " & ".join(
            [
                artist["name"]
                for artist in item_data["track"]["artists"]
            ]
        )
