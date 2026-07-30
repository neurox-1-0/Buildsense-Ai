from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def recommendation_document(payload: dict[str, Any]) -> dict[str, Any]:
    return {**payload, "created_at": utc_now()}
