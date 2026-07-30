POSITIVE = {"good", "great", "love", "excellent", "affordable", "helpful", "best", "delicious", "friendly", "fast", "fresh"}
NEGATIVE = {"bad", "poor", "expensive", "overheating", "problem", "issue", "concern", "slow", "limited", "late", "cold"}

def analyze_sentiment(text: str) -> str:
    words = set(text.lower().replace(",", " ").replace(".", " ").split())
    score = len(words & POSITIVE) - len(words & NEGATIVE)
    return "positive" if score > 0 else "negative" if score < 0 else "neutral"
