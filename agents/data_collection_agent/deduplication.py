import hashlib
from core.utils import clean_text


def deduplicate(items: list[dict]) -> list[dict]:
    seen = set()
    output = []
    for item in items:
        normalized = clean_text(item.get("content", "")).lower()
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        if normalized and digest not in seen:
            seen.add(digest)
            output.append(item)
    return output
