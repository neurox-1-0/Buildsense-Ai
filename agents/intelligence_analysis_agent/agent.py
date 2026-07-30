"""Convert public evidence into structured customer and market intelligence."""

import json
from tools.openai_client import OpenAIClient
from prompts.intelligence_prompts import INTELLIGENCE_SYSTEM_PROMPT
from schemas.intelligence_schema import IntelligenceReport
from agents.intelligence_analysis_agent.spam_filter import filter_spam
from agents.intelligence_analysis_agent.sentiment_analysis import analyze_sentiment
from agents.intelligence_analysis_agent.pain_point_extractor import extract_pain_points
from agents.intelligence_analysis_agent.purchase_intent_detector import detect_purchase_intent
from agents.intelligence_analysis_agent.trend_detector import detect_trends
from agents.intelligence_analysis_agent.confidence_scorer import score_confidence


class IntelligenceAnalysisAgent:
    def __init__(self) -> None:
        self.openai = OpenAIClient()

    def run(self, objective: dict, evidence: list[dict]) -> dict:
        evidence = filter_spam(evidence)
        compact = [
            {
                "item_id": i["item_id"],
                "source": i["source"],
                "title": i.get("title", ""),
                "url": i.get("url", ""),
                "metadata": {
                    key: (i.get("metadata") or {}).get(key)
                    for key in (
                        "place_name",
                        "formatted_address",
                        "rating",
                        "user_rating_count",
                        "primary_type",
                    )
                    if (i.get("metadata") or {}).get(key) is not None
                },
                "content": i["content"][:1200],
            }
            for i in evidence
        ]
        ai_result = self.openai.json_response(
            INTELLIGENCE_SYSTEM_PROMPT,
            json.dumps({"objective": objective, "evidence": compact}, ensure_ascii=False),
        )
        if ai_result:
            try:
                report = IntelligenceReport.model_validate(ai_result).model_dump()
                valid_ids = {item["item_id"] for item in evidence}
                for item in report["items"]:
                    item["evidence_ids"] = [
                        evidence_id for evidence_id in item["evidence_ids"]
                        if evidence_id in valid_ids
                    ]
                for field in (
                    "verified_signals",
                    "hypotheses",
                    "competitor_signals",
                    "location_signals",
                    "demand_signals",
                    "opportunity_insights",
                    "location_candidates",
                ):
                    for item in report.get(field, []):
                        item["evidence_ids"] = [
                            evidence_id for evidence_id in item.get("evidence_ids", [])
                            if evidence_id in valid_ids
                        ]
                available_locations = {
                    (
                        (item.get("metadata") or {}).get("place_name"),
                        (item.get("metadata") or {}).get("formatted_address"),
                    )
                    for item in evidence
                    if (item.get("metadata") or {}).get("place_name")
                }
                report["location_candidates"] = [
                    candidate
                    for candidate in report.get("location_candidates", [])
                    if (candidate.get("name"), candidate.get("address")) in available_locations
                ]
                objective_text = " ".join(
                    str(objective.get(key, ""))
                    for key in ("title", "description", "industry", "target_market")
                ).lower()
                location_requested = any(
                    term in objective_text
                    for term in ("location", "where", "area", "city", "suitable place", "place to open")
                )
                if location_requested and not report["location_candidates"]:
                    report["confidence"] = min(report["confidence"], 0.5)
                    report["decision_readiness"] = "low"
                    if not any(
                        "location" in gap.get("missing_information", "").lower()
                        for gap in report.get("research_gaps", [])
                    ):
                        report.setdefault("research_gaps", []).append({
                            "missing_information": "Concrete comparable location evidence",
                            "decision_impact": "A named location recommendation would otherwise be unsupported.",
                            "next_research_action": "Collect named places and addresses from a location source before selecting the site.",
                        })
                if report["items"] and not any(item["evidence_ids"] for item in report["items"]):
                    raise ValueError("AI analysis did not cite any valid evidence records")
                report["analysis_engine"] = "openai"
                return report
            except Exception:
                pass
        report = self._local_analysis(objective, evidence)
        report["analysis_engine"] = "local_rules"
        return report

    def _local_analysis(self, objective: dict, evidence: list[dict]) -> dict:
        items = []
        sentiments = []
        for entry in evidence:
            sentiment = analyze_sentiment(entry["content"])
            sentiments.append(sentiment)
            pains = extract_pain_points(entry["content"])
            needs = []
            lower = entry["content"].lower()
            need_signals = {
                "affordable pricing": ["affordable", "lower price", "cheap", "expensive"],
                "student discount": ["student discount", "student offer"],
                "family combo": ["family combo", "family deal"],
                "combo packages": ["combo offer", "combo package", "combo deal"],
                "installment plan": ["installment", "monthly payment"],
                "fast delivery": ["fast delivery", "slow delivery", "delivery time"],
                "late night delivery": ["late-night delivery", "late night delivery", "open late"],
                "online ordering": ["online ordering", "order online", "mobile ordering"],
                "vegetarian options": ["vegetarian", "veggie options"],
                "more toppings": ["more toppings", "limited toppings"],
                "large portions": ["large portions", "portion size"],
                "cheese-loaded options": ["more cheese", "extra cheese", "cheese loaded"],
                "16 GB RAM": ["16 gb ram", "16gb ram"],
                "longer warranty": ["longer warranty", "warranty"],
                "upgradeability": ["upgradeability", "upgrade options"],
                "good cooling": ["cooling", "overheating"],
                "battery life": ["battery life"],
                "after-sales support": ["after-sales", "after sales", "support"],
            }
            for need, signals in need_signals.items():
                if any(signal in lower for signal in signals):
                    needs.append(need)
            items.append({
                "topic": entry.get("title") or "Customer feedback",
                "sentiment": sentiment,
                "pain_points": pains,
                "customer_needs": needs,
                "brands": [],
                "purchase_intent": detect_purchase_intent(entry["content"]),
                "evidence_ids": [entry["item_id"]],
                "confidence": 0.72 if pains or needs else 0.58,
            })
        source_count = len(set(i["source"] for i in evidence))
        confidence = score_confidence(len(evidence), source_count, len(items))
        negative = sentiments.count("negative")
        positive = sentiments.count("positive")
        overall = "negative" if negative > positive else "positive" if positive > negative else "mixed"
        trends = detect_trends(evidence)
        top_needs = list(dict.fromkeys(
            need
            for item in items
            for need in item["customer_needs"]
        ))[:8]
        pain_points = list(dict.fromkeys(
            pain
            for item in items
            for pain in item["pain_points"]
        ))[:8]
        target_market = objective.get("target_market", "")
        target_segments = [target_market] if target_market else []
        objective_text = " ".join(
            str(objective.get(key, ""))
            for key in ("title", "description", "industry", "target_market")
        ).lower()
        all_text = " ".join(entry.get("content", "") for entry in evidence).lower()
        product_candidates = {
            "Vitamin D": ["vitamin d"],
            "Omega-3 supplements": ["omega-3", "omega 3"],
            "Blood glucose test strips": ["glucose test strip", "blood glucose strip"],
            "Baby formula": ["baby formula", "infant formula"],
            "Immunity supplements": ["immunity booster", "immunity supplement"],
            "Affordable pizza": ["affordable pizza"],
            "Family combo": ["family combo"],
            "Cheese-loaded pizza": ["cheese loaded", "more cheese"],
            "Student laptops": ["student laptop"],
            "Gaming laptops": ["gaming laptop"],
        }
        category_candidates = {
            "Diabetes care": ["diabetes", "glucose", "insulin"],
            "Heart health": ["heart health", "blood pressure", "omega-3", "omega 3"],
            "Children's medicine and baby care": ["children's medicine", "child medicine", "baby care", "baby formula"],
            "Vitamins and supplements": ["vitamin", "supplement", "immunity"],
            "Family meals": ["family combo", "family meal"],
            "Delivery and online ordering": ["delivery", "online ordering"],
            "Education laptops": ["student laptop", "university laptop"],
            "Gaming and performance": ["gaming laptop", "graphics", "performance"],
        }
        trending_products = [
            label for label, signals in product_candidates.items()
            if any(signal in all_text for signal in signals)
        ][:8]
        high_demand_categories = [
            label for label, signals in category_candidates.items()
            if any(signal in all_text for signal in signals)
        ][:8]
        def supporting_ids(terms: list[str]) -> list[str]:
            return [
                entry["item_id"]
                for entry in evidence
                if any(
                    term.lower() in f"{entry.get('title', '')} {entry.get('content', '')}".lower()
                    for term in terms
                )
            ][:12]

        verified_signals = []
        for trend in trends[:6]:
            ids = supporting_ids([trend])
            if ids:
                verified_signals.append({
                    "signal": f"Evidence repeatedly references {trend}",
                    "interpretation": f"{trend.title()} should be included in the next business validation.",
                    "evidence_ids": ids,
                    "confidence": min(0.9, 0.55 + (len(ids) * 0.06)),
                })

        demand_signals = []
        purchase_items = [
            item for item in items
            if item["purchase_intent"] in {"high", "medium"}
        ]
        if purchase_items:
            purchase_ids = list(dict.fromkeys(
                evidence_id
                for item in purchase_items
                for evidence_id in item["evidence_ids"]
            ))
            demand_signals.append({
                "signal": f"{len(purchase_items)} analyzed records contain purchase-intent language",
                "interpretation": "There is a demand signal worth testing, but it is not proof of conversion.",
                "evidence_ids": purchase_ids[:12],
                "confidence": min(0.88, 0.5 + len(purchase_items) * 0.04),
            })

        competitor_terms = ["competitor", "alternative", "compared", "better than", "other shop", "other store"]
        competitor_ids = supporting_ids(competitor_terms)
        competitor_signals = [{
            "signal": "Customers compare the offer with competing or substitute options",
            "interpretation": "Positioning should address the comparison criteria visible in the cited evidence.",
            "evidence_ids": competitor_ids,
            "confidence": min(0.85, 0.5 + len(competitor_ids) * 0.05),
        }] if competitor_ids else []

        location_terms = ["location", "near", "parking", "area", "distance", "traffic", "delivery"]
        location_ids = supporting_ids(location_terms)
        location_signals = [{
            "signal": "Evidence includes location, access, or delivery considerations",
            "interpretation": "Site or service-area selection should validate convenience alongside cost and competition.",
            "evidence_ids": location_ids,
            "confidence": min(0.85, 0.5 + len(location_ids) * 0.05),
        }] if location_ids else []
        location_groups = {}
        for entry in evidence:
            metadata = entry.get("metadata") or {}
            place_name = metadata.get("place_name")
            address = metadata.get("formatted_address")
            if not place_name or not address:
                continue
            key = (place_name, address)
            group = location_groups.setdefault(key, {
                "name": place_name,
                "address": address,
                "rating": metadata.get("rating"),
                "user_rating_count": metadata.get("user_rating_count"),
                "evidence_ids": [],
                "positive": 0,
                "negative": 0,
            })
            group["evidence_ids"].append(entry["item_id"])
            sentiment = analyze_sentiment(entry.get("content", ""))
            group["positive"] += sentiment == "positive"
            group["negative"] += sentiment == "negative"
        location_candidates = []
        for group in location_groups.values():
            review_count = len(group["evidence_ids"])
            rating_text = (
                f", rating {group['rating']}/5"
                if group["rating"] is not None else ""
            )
            location_candidates.append({
                "name": group["name"],
                "address": group["address"],
                "rating": group["rating"],
                "user_rating_count": group["user_rating_count"],
                "suitability_reason": (
                    f"Comparable local demand evidence is available from {review_count} cited reviews"
                    f"{rating_text}. Treat this as an area/competitor signal, then verify the exact site economics."
                ),
                "evidence_ids": list(dict.fromkeys(group["evidence_ids"]))[:12],
                "confidence": min(0.9, 0.5 + review_count * 0.05),
            })
        location_candidates.sort(
            key=lambda item: (
                item["rating"] if item["rating"] is not None else 0,
                item["user_rating_count"] if item["user_rating_count"] is not None else 0,
                len(item["evidence_ids"]),
            ),
            reverse=True,
        )

        hypotheses = []
        if top_needs:
            ids = list(dict.fromkeys(
                evidence_id
                for item in items
                if item["customer_needs"]
                for evidence_id in item["evidence_ids"]
            ))
            hypotheses.append({
                "signal": f"An offer centered on {', '.join(top_needs[:3])} may improve customer response",
                "interpretation": "This is a testable proposition, not a proven commercial outcome.",
                "evidence_ids": ids[:12],
                "confidence": min(0.78, confidence),
            })

        contradictions = []
        if positive and negative:
            contradictions.append(
                f"Evidence contains both positive ({positive}) and negative ({negative}) experiences; segment-level causes should be investigated."
            )
        if len(set(i["source"] for i in evidence)) <= 1 and len(evidence) > 1:
            contradictions.append(
                "Multiple records come from one source type, so apparent agreement may not represent the wider market."
            )

        opportunity_insights = []
        for need in top_needs[:3]:
            ids = supporting_ids([need])
            if ids:
                opportunity_insights.append({
                    "opportunity": f"Test an offer that directly addresses {need}",
                    "why_it_matters": "This need appears in collected customer evidence and can be validated through behavior.",
                    "recommended_test": "Run a limited pilot and measure conversion, objections, satisfaction, and repeat demand.",
                    "evidence_ids": ids,
                    "confidence": min(0.85, 0.55 + len(ids) * 0.05),
                })

        key_risks = list(dict.fromkeys(
            pain_points[:5]
            + (["Evidence is concentrated in too few source types"] if source_count < 2 else [])
            + (["Observed interest may not convert into paid demand"] if demand_signals else [])
        ))
        research_gaps = []
        if source_count < 3:
            research_gaps.append({
                "missing_information": "Independent evidence from at least three productive source types",
                "decision_impact": "Limited source diversity can bias demand and customer-priority conclusions.",
                "next_research_action": "Collect a different source type and compare whether the same needs recur.",
            })
        if not demand_signals:
            research_gaps.append({
                "missing_information": "Observed willingness to pay or purchase behavior",
                "decision_impact": "Interest alone cannot establish commercial demand.",
                "next_research_action": "Run customer interviews, preorder, quotation, landing-page, or limited-sales tests.",
            })
        location_requested = any(
            term in objective_text
            for term in ("location", "where", "area", "city", "suitable place", "place to open")
        )
        if location_requested and not location_candidates:
            research_gaps.append({
                "missing_information": "Comparable location-level footfall, access, rent, and competitor data",
                "decision_impact": "A precise site recommendation would otherwise be speculative.",
                "next_research_action": "Score at least three candidate areas using the same location criteria and observation periods.",
            })
        if location_requested and not location_candidates:
            confidence = min(confidence, 0.5)
        readiness = (
            "high" if confidence >= 0.75 and source_count >= 3 and len(evidence) >= 8
            else "medium" if confidence >= 0.55 and source_count >= 2
            else "low"
        )
        next_actions = [gap["next_research_action"] for gap in research_gaps[:3]]
        if not next_actions:
            next_actions = [
                "Validate the highest-ranked opportunity with a limited real-customer pilot.",
                "Monitor conversion, margin, satisfaction, objections, and repeat behavior before scaling.",
            ]
        return IntelligenceReport(
            summary=f"Analyzed {len(evidence)} evidence items and identified demand signals around {', '.join(trends[:3]) or 'value, reliability, and support'}.",
            items=items,
            trends=trends,
            top_customer_needs=top_needs or trends[:5],
            pain_points=pain_points,
            target_segments=target_segments,
            data_sources_used=sorted({entry.get("source", "unknown") for entry in evidence}),
            trending_products=trending_products,
            high_demand_categories=high_demand_categories,
            overall_sentiment=overall,
            confidence=confidence,
            verified_signals=verified_signals,
            hypotheses=hypotheses,
            contradictions=contradictions,
            competitor_signals=competitor_signals,
            location_signals=location_signals,
            demand_signals=demand_signals,
            opportunity_insights=opportunity_insights,
            key_risks=key_risks,
            research_gaps=research_gaps,
            next_best_research_actions=next_actions,
            decision_readiness=readiness,
            location_candidates=location_candidates[:5],
        ).model_dump()
