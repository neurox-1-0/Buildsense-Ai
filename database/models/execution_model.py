from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def execution_document(
    execution_id: str,
    objective_id: str,
    human_guidance: str = "",
    parent_execution_id: str | None = None,
) -> dict[str, Any]:
    now = utc_now()
    return {
        "execution_id": execution_id,
        "objective_id": objective_id,
        "parent_execution_id": parent_execution_id,
        "human_guidance": human_guidance,
        "status": "queued",
        "current_node": "queued",
        "retry_count": 0,
        "error": None,
        "created_at": now,
        "updated_at": now,
    }
