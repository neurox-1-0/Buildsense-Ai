PAIN_POINTS = [
    "overheating",
    "battery life",
    "price",
    "expensive",
    "warranty",
    "after-sales support",
    "performance",
    "availability",
    "upgrade options",
    "slow delivery",
    "long waiting time",
    "limited toppings",
    "limited options",
    "few vegetarian options",
    "delivery coverage",
    "poor service",
    "inconsistent quality",
]

def extract_pain_points(text: str) -> list[str]:
    lower = text.lower()
    return [point for point in PAIN_POINTS if point in lower]
