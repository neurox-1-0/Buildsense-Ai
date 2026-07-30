import requests
from config.settings import get_settings
from core.exceptions import ExternalToolError
from core.url_safety import validate_public_url


class FirecrawlClient:
    URL = "https://api.firecrawl.dev/v1/scrape"

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def available(self) -> bool:
        return bool(self.settings.firecrawl_api_key)

    def scrape(self, url: str) -> dict | None:
        validate_public_url(url)
        if not self.available:
            return None
        headers = {"Authorization": f"Bearer {self.settings.firecrawl_api_key}", "Content-Type": "application/json"}
        try:
            response = requests.post(self.URL, headers=headers, json={"url": url, "formats": ["markdown"]}, timeout=self.settings.request_timeout_seconds)
            response.raise_for_status()
            data = response.json().get("data", response.json())
            return {"source": "firecrawl", "title": data.get("metadata", {}).get("title", ""), "content": data.get("markdown", ""), "author": "", "published_at": None, "url": url}
        except requests.RequestException as exc:
            raise ExternalToolError(f"Firecrawl request failed: {exc}") from exc
