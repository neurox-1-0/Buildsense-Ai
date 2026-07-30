import json
from pathlib import Path

from tools.scraper_client import ScraperClient


def main() -> int:
    path = Path(__file__).resolve().parents[1] / "docs" / "demo_objectives.json"
    objectives = json.loads(path.read_text(encoding="utf-8"))
    client = ScraperClient()
    failed = False
    for objective in objectives:
        for url in objective.get("source_urls", []):
            try:
                item = client.scrape(url)
                length = len(item.get("content", ""))
                status = "usable" if length >= 200 else "too_short"
                failed = failed or status != "usable"
                print(json.dumps({"url": url, "status": status, "content_chars": length}))
            except Exception as exc:
                failed = True
                print(json.dumps({"url": url, "status": "failed", "error": str(exc)}))
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
