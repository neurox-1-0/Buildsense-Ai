from tools.scraper_client import ScraperClient


class ScraperSource:
    name = "scraper"

    def __init__(self):
        self.client = ScraperClient()

    def collect(self, urls: list[str], limit: int):
        return [self.client.scrape(url) for url in urls[:limit]]
