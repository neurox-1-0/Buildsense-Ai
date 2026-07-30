"""Plan and collect public market evidence using enabled research tools."""

import logging
import hashlib
from config.settings import get_settings
from core.utils import new_id
from agents.data_collection_agent.deduplication import deduplicate
from agents.data_collection_agent.validator import validate_items
from agents.data_collection_agent.sources.youtube_source import YouTubeSource
from agents.data_collection_agent.sources.google_places_source import GooglePlacesSource
from agents.data_collection_agent.sources.firecrawl_source import FirecrawlSource
from agents.data_collection_agent.sources.scraper_source import ScraperSource

logger = logging.getLogger(__name__)

DEMO_ITEMS = [
    {"source": "demo", "title": "Student laptop discussion", "content": "I need an affordable gaming laptop for university work, but battery life and overheating are major concerns.", "author": "demo-user-1", "url": ""},
    {"source": "demo", "title": "Budget gaming laptop review", "content": "A student discount, installment plan, 16 GB RAM, and a longer warranty would make this laptop easier to buy.", "author": "demo-user-2", "url": ""},
    {"source": "demo", "title": "Retail feedback", "content": "The performance is good, but after-sales support and upgrade options matter as much as the graphics card.", "author": "demo-user-3", "url": ""},
    {"source": "demo", "title": "Campus buyer feedback", "content": "I compare price, cooling, battery, RAM upgradeability, and warranty before purchasing a gaming laptop.", "author": "demo-user-4", "url": ""},
]


class DataCollectionAgent:
    def __init__(self) -> None:
        self.settings = get_settings()

    def run(self, objective: dict, plan: dict) -> dict:
        query = plan.get("query") or " ".join(objective.get("keywords") or [objective["title"]])
        urls = objective.get("source_urls", [])
        items = []
        errors = []
        tool_results = []
        trace_events = []

        operations = {
            "youtube": lambda: YouTubeSource().collect(query, self.settings.max_source_items),
            "google_places": lambda: GooglePlacesSource().collect(query, 10),
            "firecrawl": lambda: FirecrawlSource().collect(urls, 5),
            "scraper": lambda: ScraperSource().collect(urls, 5),
        }
        selected_tools = plan.get("preferred_tools") or []

        for name in selected_tools:
            operation = operations.get(name)
            if not operation:
                errors.append({"source": name, "error": "Unknown tool selected by planner"})
                continue
            try:
                raw_items = [item for item in operation() if item]
                items.extend(raw_items)
                result = {
                    "tool": name,
                    "status": "productive" if raw_items else "empty",
                    "input": {"query": query} if name in {"youtube", "google_places"} else {"urls": urls[:5]},
                    "output_count": len(raw_items),
                    "output_preview": [
                        {
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "content_excerpt": (item.get("content") or "")[:240],
                        }
                        for item in raw_items[:3]
                    ],
                    "output_hashes": [
                        hashlib.sha256(
                            (item.get("content") or "").encode("utf-8")
                        ).hexdigest()
                        for item in raw_items
                    ],
                }
                tool_results.append(result)
                trace_events.append({
                    "step": "tool_call",
                    "message": (
                        f"{name} contributed {len(raw_items)} evidence records"
                        if raw_items
                        else f"{name} completed but returned no usable evidence"
                    ),
                    "data": result,
                })
            except Exception as exc:
                logger.warning("Source %s failed: %s", name, exc)
                error = {"source": name, "error": str(exc), "query": query}
                errors.append(error)
                tool_results.append({"tool": name, "status": "failed", **error})
                trace_events.append({
                    "step": "tool_failure",
                    "message": f"{name} failed; the workflow will evaluate recovery",
                    "data": error,
                })

        demo_used = False
        if len(items) < self.settings.min_evidence_items and self.settings.enable_demo_data:
            demo_used = True
            items.extend([{**item, "metadata": {"is_demo": True}} for item in DEMO_ITEMS])
            trace_events.append({
                "step": "demo_fallback",
                "message": "Clearly labelled synthetic demonstration evidence was added",
                "data": {"synthetic": True, "count": len(DEMO_ITEMS)},
            })

        received_count = len(items)
        items = validate_items(deduplicate(items))[: self.settings.max_source_items]
        for item in items:
            item.setdefault("item_id", new_id("RAW"))
            item.setdefault("metadata", {})
            item["metadata"].setdefault("is_demo", False)
            item["metadata"]["collection_query"] = query
            item["metadata"]["collection_attempt"] = plan.get("attempt", 1)
            item["metadata"]["content_sha256"] = hashlib.sha256(
                (item.get("content") or "").encode("utf-8")
            ).hexdigest()
            item.setdefault("published_at", None)
            item.setdefault("author", "")
            item.setdefault("title", "")
            item.setdefault("url", "")

        trace_events.append({
            "step": "validation",
            "message": f"Accepted {len(items)} of {received_count} collected records",
            "data": {
                "received": received_count,
                "accepted": len(items),
                "duplicates_or_invalid": received_count - len(items),
                "demo_used": demo_used,
            },
        })
        return {
            "items": items,
            "errors": errors,
            "sources_used": sorted(set(i["source"] for i in items)),
            "tool_results": tool_results,
            "trace_events": trace_events,
            "demo_used": demo_used,
        }
