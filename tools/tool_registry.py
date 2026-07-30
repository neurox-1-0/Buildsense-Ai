"""Describe external evidence tools available to the agent planner."""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    purpose: str
    enabled: bool = True


TOOL_REGISTRY = {
    "youtube": ToolDefinition("youtube", "Collect YouTube videos and public comments"),
    "google_places": ToolDefinition("google_places", "Collect Google place details and supported reviews"),
    "firecrawl": ToolDefinition("firecrawl", "Extract readable content from public web pages"),
    "scraper": ToolDefinition("scraper", "Collect text from permitted public HTML pages"),
}


def enabled_tools() -> list[str]:
    return [name for name, tool in TOOL_REGISTRY.items() if tool.enabled]
