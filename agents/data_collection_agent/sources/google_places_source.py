from tools.google_places_client import GooglePlacesClient


class GooglePlacesSource:
    name = "google_places"

    def __init__(self):
        self.client = GooglePlacesClient()

    def collect(self, query: str, limit: int):
        return self.client.search_reviews(query, limit)
