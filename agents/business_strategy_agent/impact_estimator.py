def normalize_impact(strategy: dict) -> dict:
    strategy["score"] = max(0, min(100, float(strategy.get("score", 0))))
    return strategy
