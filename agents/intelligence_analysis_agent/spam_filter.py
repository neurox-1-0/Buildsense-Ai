SPAM_MARKERS = ("subscribe to my channel", "click here", "free money", "buy followers")

def filter_spam(items: list[dict]) -> list[dict]:
    return [i for i in items if not any(m in i.get("content", "").lower() for m in SPAM_MARKERS)]
