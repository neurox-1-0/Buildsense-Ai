def generate_local_strategies(objective: dict, report: dict) -> list[dict]:
    trends = report.get("trends", [])
    focus = ", ".join(trends[:3]) or "affordability, reliability, and support"
    evidence_ids = list(dict.fromkeys(
        evidence_id
        for item in report.get("items", [])
        for evidence_id in item.get("evidence_ids", [])
    ))
    market = objective.get("target_market") or "the target market"
    industry = objective.get("industry") or "the business"
    return [
        {"title": "Evidence-led value proposition", "description": f"Create a focused offer for {market} that addresses the strongest validated needs: {focus}.", "expected_impact": "High if validated in a pilot", "implementation_cost": "Medium", "risk": "Medium", "score": 86, "justification": f"Responds directly to the strongest evidence themes in {industry}.", "evidence_ids": evidence_ids},
        {"title": "Segmented pilot programme", "description": f"Test the proposed offer with a small {market} segment and measure conversion, satisfaction, and objections before scaling.", "expected_impact": "Medium with measurable learning", "implementation_cost": "Low to medium", "risk": "Low", "score": 82, "justification": "A controlled pilot limits exposure while testing whether observed intent becomes demand.", "evidence_ids": evidence_ids},
        {"title": "Service and trust differentiation", "description": f"Build messaging and operational improvements around the reliability and support needs observed for {market}.", "expected_impact": "Medium", "implementation_cost": "Medium", "risk": "Low", "score": 76, "justification": "Uses recurring pain points as differentiation instead of relying only on price.", "evidence_ids": evidence_ids},
    ]
