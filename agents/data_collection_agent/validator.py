def valid_item(item: dict) -> bool:
    return bool(item.get("source") and len((item.get("content") or "").strip()) >= 15)


def validate_items(items: list[dict]) -> list[dict]:
    return [item for item in items if valid_item(item)]
