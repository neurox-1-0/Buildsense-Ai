from tools.youtube_client import YouTubeClient


class YouTubeSource:
    name = "youtube"

    def __init__(self):
        self.client = YouTubeClient()

    def collect(self, query: str, limit: int):
        return self.client.search_comments(query, limit)
