from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def objective_document(objective_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    return {"objective_id": objective_id, **payload, "status": "created", "created_at": now, "updated_at": now}
