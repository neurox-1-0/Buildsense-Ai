HIGH = ("need", "want to buy", "planning to buy", "before purchasing", "would buy")
MEDIUM = ("consider", "compare", "interested", "looking for")

def detect_purchase_intent(text: str) -> str:
    lower = text.lower()
    if any(p in lower for p in HIGH): return "high"
    if any(p in lower for p in MEDIUM): return "medium"
    return "low"
