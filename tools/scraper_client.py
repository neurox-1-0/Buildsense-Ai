import requests
from bs4 import BeautifulSoup
from config.settings import get_settings
from core.exceptions import ExternalToolError
from core.utils import clean_text
from core.url_safety import safe_public_get


class ScraperClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def scrape(self, url: str) -> dict:
        try:
            response = safe_public_get(
                url,
                timeout=self.settings.request_timeout_seconds,
                headers={"User-Agent": "BuildSenseAI/1.0 (+research MVP)"},
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "noscript"]):
                tag.decompose()
            title = clean_text(soup.title.get_text(" ") if soup.title else "")
            content = clean_text(soup.get_text(" "))[:12000]
            return {"source": "scraper", "title": title, "content": content, "author": "", "published_at": None, "url": url}
        except requests.RequestException as exc:
            raise ExternalToolError(f"Web scrape failed: {exc}") from exc
