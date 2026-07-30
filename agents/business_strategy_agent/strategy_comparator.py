def rank_strategies(strategies: list[dict]) -> list[dict]:
    return sorted(strategies, key=lambda item: item.get("score", 0), reverse=True)
