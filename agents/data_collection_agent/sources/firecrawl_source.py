from tools.firecrawl_client import FirecrawlClient


class FirecrawlSource:
    name = "firecrawl"

    def __init__(self):
        self.client = FirecrawlClient()

    def collect(self, urls: list[str], limit: int):
        output = []
        for url in urls[:limit]:
            item = self.client.scrape(url)
            if item:
                output.append(item)
        return output
