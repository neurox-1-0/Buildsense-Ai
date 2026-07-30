"""Check whether configured external research services are reachable."""

from config.settings import get_settings
from core.url_safety import validate_public_url
from database.connection import get_database
from tools.firecrawl_client import FirecrawlClient
from tools.google_places_client import GooglePlacesClient
from tools.openai_client import OpenAIClient
from tools.scraper_client import ScraperClient
from tools.youtube_client import YouTubeClient


class ReadinessService:
    def check(self, live: bool = False, query: str = "business customer reviews", source_url: str = "") -> dict:
        settings = get_settings()
        checks = {
            "openai": self._configured(bool(settings.openai_api_key)),
            "youtube": self._configured(bool(settings.youtube_api_key)),
            "google_places": self._configured(bool(settings.google_maps_api_key)),
            "firecrawl": self._configured(bool(settings.firecrawl_api_key)),
            "direct_scraper": {"status": "ready", "configured": True},
            "storage": {
                "status": "ready",
                "configured": True,
                "mode": "memory" if settings.use_memory_db or not settings.mongodb_uri else "mongodb",
            },
        }
        get_database()
        if not live:
            return {"live_test": False, "checks": checks}

        probes = {
            "openai": lambda: OpenAIClient().json_response(
                "Return JSON only.", 'Return this JSON object: {"ready": true}.'
            ),
            "youtube": lambda: YouTubeClient().search_comments(query, 1),
            "google_places": lambda: GooglePlacesClient().search_reviews(query, 1),
        }
        if source_url:
            validate_public_url(source_url)
            probes["direct_scraper"] = lambda: ScraperClient().scrape(source_url)
            probes["firecrawl"] = lambda: FirecrawlClient().scrape(source_url)

        for name, operation in probes.items():
            if not checks[name].get("configured"):
                continue
            try:
                result = operation()
                if name in {"openai", "firecrawl", "direct_scraper"} and not result:
                    raise RuntimeError("Probe completed without a usable response")
                checks[name]["status"] = "working"
                checks[name]["result_count"] = (
                    len(result) if isinstance(result, list) else int(bool(result))
                )
            except Exception as exc:
                checks[name]["status"] = "failed"
                checks[name]["error"] = str(exc)
        return {
            "live_test": True,
            "ready_for_three_tool_demo": sum(
                check.get("status") == "working" and check.get("result_count", 0) > 0
                for name, check in checks.items()
                if name not in {"storage", "openai"}
            ) >= 3,
            "checks": checks,
        }

    @staticmethod
    def _configured(configured: bool) -> dict:
        return {
            "configured": configured,
            "status": "configured_not_tested" if configured else "unavailable",
        }
