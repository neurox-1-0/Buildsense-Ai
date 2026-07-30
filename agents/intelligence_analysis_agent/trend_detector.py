from collections import Counter

def detect_trends(items: list[dict]) -> list[str]:
    candidates = [
        "affordable",
        "student discount",
        "family combo",
        "combo offer",
        "installment",
        "fast delivery",
        "late night delivery",
        "online ordering",
        "vegetarian options",
        "large portions",
        "more cheese",
        "more toppings",
        "battery life",
        "overheating",
        "16 gb ram",
        "warranty",
        "upgrade",
        "after-sales support",
    ]
    counts = Counter()
    for item in items:
        text = item.get("content", "").lower()
        for candidate in candidates:
            if candidate in text:
                counts[candidate] += 1
    return [name for name, _ in counts.most_common(5)]
