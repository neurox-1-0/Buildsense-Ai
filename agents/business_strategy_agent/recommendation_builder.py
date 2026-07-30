import re


def _extract_requirements(objective: dict) -> list[str]:
    """Turn the user's natural-language goal into explicit decisions to answer."""
    text = " ".join(
        str(objective.get(key, ""))
        for key in ("title", "description")
        if objective.get(key)
    )
    fragments = [
        fragment.strip(" -:;,")
        for fragment in re.split(r"[?.!\n]+|\b(?:and also|also|then)\b", text, flags=re.I)
        if len(fragment.strip(" -:;,")) >= 8
    ]
    requirements = []
    for fragment in fragments:
        normalized = fragment.lower()
        if fragment not in requirements and any(
            marker in normalized
            for marker in (
                "want", "need", "find", "recommend", "identify", "choose",
                "improve", "start", "open", "sell", "target", "location",
                "price", "market", "supplier", "inventory", "customer",
            )
        ):
            requirements.append(fragment)
    return requirements[:8] or [objective.get("description") or objective.get("title", "Business decision")]


def _requirement_answer(
    requirement: str,
    objective: dict,
    needs: list[str],
    categories: list[str],
    products: list[str],
    evidence_ids: list[str],
    confidence: float,
    location_candidates: list[dict],
) -> dict:
    lower = requirement.lower()
    market = objective.get("target_market") or "the validated target customers"
    need_text = ", ".join(needs[:3]) or "the strongest validated customer needs"
    product_text = ", ".join(products[:3] or categories[:3]) or "a small validated core offer"
    validation = "Validate this recommendation with direct customer interviews and current local operating data."
    if any(term in lower for term in ("where", "location", "place", "area", "city", "open")):
        if location_candidates:
            best_location = location_candidates[0]
            recommendation = (
                f"Use {best_location['name']} at {best_location.get('address') or market} "
                "as the strongest evidence-supported location benchmark and prioritize the "
                "surrounding customer catchment for the first site shortlist."
            )
        else:
            recommendation = (
                f"Prioritize the {market} customer catchment as the recommended launch zone, "
                "with the first site placed near its highest-frequency demand generator and "
                "accessible from the main customer travel route."
            )
        rationale = (
            f"This is the strongest location conclusion supported by the target market and "
            f"collected evidence themes ({need_text})."
        )
        validation = "Before signing a lease, verify the recommended zone with footfall, rent, access, direct-competition, and conservative break-even checks."
    elif any(term in lower for term in ("supplier", "stock", "inventory", "reorder")):
        recommendation = (
            f"Pilot limited stock around {product_text}, compare multiple suppliers, and set "
            "reorder rules from observed sales, lead time, stock-outs, and margin."
        )
        rationale = "A controlled assortment limits cash exposure while real demand and supplier reliability are measured."
        validation = "Verify supplier terms, lead times, returns, compliance, and landed cost before committing inventory."
    elif any(term in lower for term in ("product", "sell", "menu", "service", "offer")):
        recommendation = (
            f"Launch with a focused portfolio built around {product_text}, including an entry "
            "option, a core offer, and one differentiated or premium option."
        )
        rationale = f"This directly responds to the strongest supported needs: {need_text}."
        validation = "Pilot the smallest viable portfolio and retain products only when conversion, margin, and repeat demand meet thresholds."
    elif any(term in lower for term in ("audience", "customer", "target", "segment", "people")):
        recommendation = (
            f"Prioritize {market}; separate early adopters, value-sensitive buyers, and "
            "repeat-value customers using their needs and purchase behavior."
        )
        rationale = f"The objective names this market and evidence highlights {need_text}."
    elif any(term in lower for term in ("market", "promot", "advert", "brand", "grow", "improve")):
        recommendation = (
            f"Build acquisition messages around {need_text}, test two measurable channels, "
            "and improve the offer weekly using conversion and customer objections."
        )
        rationale = "Evidence-led messaging and a measured pilot reduce the risk of scaling an unvalidated idea."
    elif any(term in lower for term in ("price", "cost", "budget", "profit", "revenue")):
        recommendation = (
            "Use entry, core, and premium price points, but set final prices only after "
            "validating unit cost, operating cost, competitor alternatives, and required margin."
        )
        rationale = "The system must not invent prices or financial returns without current local cost evidence."
        validation = "Collect supplier quotations and calculate contribution margin and break-even under conservative demand."
    else:
        recommendation = (
            f"Run a measured pilot for {market} centered on {need_text}, then scale only "
            "after demand, delivery feasibility, and unit economics are confirmed."
        )
        rationale = "This is the most defensible action supported by the current objective and evidence."
    return {
        "requirement": requirement,
        "recommendation": recommendation,
        "rationale": rationale,
        "evidence_ids": evidence_ids[:12],
        "confidence": round(min(0.95, max(0.35, confidence)), 2),
        "validation_needed": validation,
    }


def _dynamic_sections(
    objective: dict,
    requirement_answers: list[dict],
    evidence_ids: list[str],
    location_recommendations: list[str],
    audience_profiles: list[str],
    product_portfolio: list[str],
    pricing_strategy: list[str],
    marketing_recommendations: list[str],
    operational_improvements: list[str],
    financial_assumptions: list[str],
    ninety_day_plan: list[str],
    success_metrics: list[str],
) -> list[dict]:
    """Select report sections from the user's decision rather than a fixed template."""
    goal = " ".join(
        [objective.get("title", ""), objective.get("description", "")]
        + [item["requirement"] for item in requirement_answers]
    ).lower()
    candidates = []

    def add(title: str, purpose: str, items: list[str], measure: str) -> None:
        candidates.append({
            "title": title,
            "purpose": purpose,
            "recommendations": items[:8],
            "evidence_ids": evidence_ids[:12],
            "success_measure": measure,
        })

    location_requested = (
        any(term in goal for term in ("location", "where", "place", "area", "city"))
        or ("open" in goal and any(term in goal for term in (" near ", " in ", " at ")))
    )
    if location_requested:
        add("Location decision", "Choose and validate a suitable operating area.", location_recommendations, "A scored shortlist with verified footfall, occupancy cost, access, and competition.")
    if any(term in goal for term in ("audience", "customer", "target", "segment", "people", "market")):
        add("Customer and audience strategy", "Define who to serve first and why.", audience_profiles, "Conversion, repeat rate, and satisfaction by customer segment.")
    if any(term in goal for term in ("product", "sell", "menu", "service", "offer", "business", "start")):
        add("Offer and product design", "Build the smallest portfolio that solves validated needs.", product_portfolio, "Product-level conversion, contribution margin, and repeat demand.")
    if any(term in goal for term in ("price", "cost", "budget", "profit", "revenue", "sell", "product")):
        add("Pricing and commercial model", "Create sustainable price points without unsupported forecasts.", pricing_strategy, "Contribution margin, average transaction value, and break-even progress.")
    if any(term in goal for term in ("market", "promot", "advert", "brand", "customer", "grow", "improve")):
        add("Growth and customer acquisition", "Reach the selected audience with measurable messages and channels.", marketing_recommendations, "Acquisition cost, qualified leads, conversion, and repeat customers.")
    if any(term in goal for term in ("operation", "improve", "service", "delivery", "staff", "supplier", "inventory", "stock")):
        add("Operating model", "Deliver the promise consistently and control execution risk.", operational_improvements, "Waiting time, complaints, stock-outs or capacity, and resolution time.")
    if any(term in goal for term in ("budget", "cost", "profit", "finance", "start", "open", "business")):
        add("Financial validation", "Test affordability and downside before committing capital.", financial_assumptions, "Verified unit economics, break-even assumptions, cash runway, and pilot-loss limit.")
    add("Action roadmap", "Turn the recommendation into staged decisions.", ninety_day_plan, "Every phase ends with a documented continue, revise, relocate, or stop decision.")
    add("Decision scorecard", "Measure whether the business change is working.", success_metrics, "A weekly dashboard with owners, baselines, targets, and corrective actions.")
    return candidates[:7]


def build_recommendation(strategies: list[dict], report: dict, objective: dict) -> dict:
    ranked = sorted(strategies, key=lambda item: item.get("score", 0), reverse=True)
    best = ranked[0]
    needs = report.get("top_customer_needs") or report.get("trends", [])[:5]
    target_markets = report.get("target_segments") or [
        objective.get("target_market") or "Target customers identified during validation"
    ]
    opportunity_score = round(
        min(95, max(35, report.get("confidence", 0.5) * 100 + best.get("score", 50) * 0.15)),
        1,
    )
    industry_text = f"{objective.get('industry', '')} {objective.get('description', '')}".lower()
    title_text = objective.get("title", "")
    market_label = ", ".join(target_markets[:3])
    categories = report.get("high_demand_categories") or report.get("trends", [])[:5]
    trending_products = report.get("trending_products") or report.get("trends", [])[:5]
    complaints = report.get("pain_points") or [
        "Insufficient evidence to rank specific customer complaints"
    ]
    evidence_ids = list(dict.fromkeys(
        evidence_id
        for item in report.get("items", [])
        for evidence_id in item.get("evidence_ids", [])
    ))
    if any(term in industry_text for term in ("pharmacy", "inventory", "retail", "stock")):
        recommended_changes = [
            *[
                f"Increase safety stock and monitor weekly demand for {item}"
                for item in trending_products[:4]
            ],
            "Set reorder thresholds from recent sales and out-of-stock frequency",
            "Pilot new products before committing to large purchase volumes",
        ]
    else:
        recommended_changes = [
            f"Prioritize an offer around {item}" for item in needs[:4]
        ] + ["Validate demand with a limited launch before scaling"]
    marketing_recommendations = [
        f"Build targeted campaigns for {market}" for market in target_markets[:3]
    ] + [
        "Use educational content built around the strongest customer needs",
        "Create a loyalty or repeat-purchase programme",
        "Measure campaign conversion before increasing spend",
    ]
    operational_improvements = [
        "Track demand, availability, and customer complaints in one weekly dashboard",
        "Reduce waiting time at the highest-friction customer touchpoints",
        "Notify customers when unavailable products or services return",
        "Offer digital ordering, reservations, or pickup where operationally suitable",
    ]
    is_food_business = any(
        term in industry_text
        for term in ("coffee", "cafe", "café", "restaurant", "food", "bakery", "beverage")
    )
    is_retail_business = any(
        term in industry_text
        for term in ("retail", "shop", "store", "pharmacy", "inventory")
    )
    location_recommendations = [
        f"Shortlist areas with frequent access to {market_label}; compare weekday, evening, and weekend footfall.",
        "Score each candidate site for visibility, access, parking or transit, nearby demand generators, rent, and direct competition.",
        "Validate the top two locations with manual footfall counts and short customer interviews before signing a lease.",
        "Choose a site only when conservative sales capacity can cover occupancy and staffing costs.",
    ]
    if report.get("location_candidates"):
        top_location = report["location_candidates"][0]
        location_recommendations.insert(
            0,
            f"Recommended evidence-supported benchmark: {top_location['name']}, "
            f"{top_location.get('address') or market_label}. "
            f"{top_location.get('suitability_reason', '')}".strip(),
        )
    if is_food_business:
        location_recommendations.insert(
            1,
            "Prioritize sites near offices, campuses, residential clusters, or transport nodes with morning and afternoon demand.",
        )
    audience_profiles = [
        f"Primary audience — {market}: prioritize the needs {', '.join(needs[:3]) or 'identified in validation'}."
        for market in target_markets[:3]
    ] or ["Define a primary audience from live interviews before launch."]
    audience_profiles += [
        "Early adopters — customers actively comparing alternatives or expressing purchase intent.",
        "Repeat-value segment — customers most likely to return when service, convenience, and reliability are consistent.",
    ]
    if is_food_business:
        product_portfolio = [
            "Core menu — a small set of reliable high-frequency drinks or meals built around validated demand.",
            "Entry offer — an affordable product that lowers the barrier for first-time customers.",
            "Signature offer — a distinctive high-margin item that makes the business memorable.",
            "Add-ons — snacks, upgrades, extras, or bundles that increase average order value.",
            "Dietary and convenience options — include only those supported by local validation.",
            "Seasonal test — rotate one limited product and retain it only if repeat demand is demonstrated.",
        ]
    elif is_retail_business:
        product_portfolio = [
            f"Core assortment — prioritize validated categories: {', '.join(categories[:3]) or 'highest-frequency customer needs'}.",
            "Entry-price option — serve price-sensitive customers without obscuring quality or warranty terms.",
            "Mid-tier recommended option — balance value, reliability, and margin.",
            "Premium option — serve customers who value performance, convenience, or service.",
            "Add-ons and bundles — combine complementary products only where they solve a documented need.",
            "Pilot inventory — test new items in limited quantities before scaling stock.",
        ]
    else:
        product_portfolio = [
            f"Core offer — solve {', '.join(needs[:3]) or 'the strongest validated needs'}.",
            "Entry offer — a low-commitment way for customers to test the value proposition.",
            "Primary offer — the best balance of customer value, delivery feasibility, and margin.",
            "Premium or service-enhanced offer — provide additional convenience, support, or customization.",
            "Pilot add-on — test one complementary offer and retain it only after measured demand.",
        ]
    pricing_strategy = [
        "Benchmark direct and substitute competitors, but set prices from delivered value and sustainable unit economics.",
        "Create clear entry, core, and premium price points so customers can self-select.",
        "Test one bundle or loyalty incentive without permanently discounting the main offer.",
        "Track gross margin, conversion, average order value, and repeat purchase before changing prices.",
        "Do not publish unsupported price promises; validate supplier, tax, delivery, and operating costs first.",
    ]
    customer_experience_plan = [
        "Design a simple discovery-to-purchase journey with clear products, prices, availability, and support terms.",
        "Set service standards for response time, waiting time, issue resolution, and follow-up.",
        "Collect feedback at purchase and after use; classify complaints weekly and assign corrective actions.",
        "Create a repeat-customer mechanism such as loyalty credit, reminders, memberships, or personalized follow-up.",
    ]
    technology_plan = [
        "Use a point-of-sale or order system that records product, time, channel, discounts, and customer segment.",
        "Maintain a weekly dashboard for sales, margin, inventory or capacity, complaints, and campaign conversion.",
        "Provide digital discovery and ordering through the channels customers already use.",
        "Protect customer information with role-based access, backups, and minimal data collection.",
    ]
    financial_assumptions = [
        "Build a conservative base-case budget covering setup, deposits, equipment, initial inventory, licences, marketing, payroll, and working capital.",
        "Calculate unit economics before launch: selling price minus product, packaging, payment, delivery, and variable service costs.",
        "Estimate break-even from contribution margin and fixed monthly costs; do not treat the opportunity score as a revenue forecast.",
        "Keep a contingency reserve and define a maximum pilot-loss limit before committing capital.",
    ]
    ninety_day_plan = [
        "Days 1–15 — validate locations, interview target customers, map competitors, and confirm legal and supplier requirements.",
        "Days 16–30 — finalize the minimum viable offer, pricing hypotheses, operating process, budget, and success thresholds.",
        "Days 31–60 — launch a limited pilot, record every sale and objection, and test two acquisition channels.",
        "Days 61–75 — improve weak products, service bottlenecks, pricing, and messaging using pilot evidence.",
        "Days 76–90 — decide to scale, revise, relocate, or stop based on the predefined metrics and cash-risk limit.",
    ]
    success_metrics = [
        "Qualified customer conversations and purchase conversion rate",
        "Revenue, gross margin, and contribution margin by product or service",
        "Average transaction value and attach or bundle rate",
        "Repeat purchase or returning-customer rate",
        "Customer satisfaction, complaint rate, and resolution time",
        "Inventory waste, stock-outs, capacity utilization, or service waiting time",
        "Acquisition cost and conversion by marketing channel",
        "Actual cash burn versus the approved pilot budget",
    ]
    immediate_next_actions = [
        f"Convert '{title_text or 'the business idea'}' into three measurable assumptions: customer, problem, and willingness to pay.",
        "Select three candidate locations or delivery areas and complete the location scorecard.",
        "Interview at least ten target customers using the same question set.",
        "Request real supplier and operating-cost quotations before setting final prices.",
        "Define pilot budget, launch date, owner, metrics, and stop/go thresholds.",
    ]
    requirements = _extract_requirements(objective)
    requirement_answers = [
        _requirement_answer(
            requirement,
            objective,
            needs,
            categories,
            trending_products,
            evidence_ids,
            report.get("confidence", 0.5),
            report.get("location_candidates", []),
        )
        for requirement in requirements
    ]
    dynamic_sections = _dynamic_sections(
        objective,
        requirement_answers,
        evidence_ids,
        location_recommendations,
        audience_profiles,
        product_portfolio,
        pricing_strategy,
        marketing_recommendations,
        operational_improvements,
        financial_assumptions,
        ninety_day_plan,
        success_metrics,
    )
    overall_recommendation = (
        f"Prioritize '{best['title']}' for {', '.join(target_markets[:3])}. "
        f"Address {', '.join(needs[:3]) or 'the strongest validated customer needs'} "
        "through a measured pilot, monitor customer response, and scale only after "
        "the demand and operational assumptions are confirmed."
    )
    return {
        "summary": f"Prioritize '{best['title']}' while testing the strongest alternative in a smaller pilot.",
        "recommended_strategy": best,
        "alternatives": ranked[1:],
        "confidence": min(0.95, max(0.5, report.get("confidence", 0.5) + 0.08)),
        "evidence_summary": report.get("trends", [])[:5],
        "final_business_report": {
            "business_goal": objective.get("description") or objective.get("title", ""),
            "opportunity_score": opportunity_score,
            "confidence": round(report.get("confidence", 0.5) * 100, 1),
            "data_sources_used": report.get("data_sources_used", []),
            "top_customer_complaints": complaints[:8],
            "trending_products": trending_products[:8],
            "high_demand_categories": categories[:8],
            "recommended_business_changes": recommended_changes[:8],
            "marketing_recommendations": marketing_recommendations[:8],
            "operational_improvements": operational_improvements[:8],
            "overall_recommendation": overall_recommendation,
            "target_markets": target_markets[:6],
            "top_customer_needs": needs[:8],
            "competitive_advantages": [
                "Offer designed around validated customer needs",
                "Pilot-led launch with measurable customer feedback",
                "Clear value, service, and trust differentiation",
            ],
            "recommended_launch_strategy": [
                best["title"],
                "Run a limited market pilot",
                "Measure conversion, satisfaction, and objections",
                "Refine the offer before scaling",
            ],
            "key_risks": list(dict.fromkeys(
                report.get("key_risks", [])[:5]
                + report.get("pain_points", [])[:4]
                + [best.get("risk", "Market validation risk")]
            )),
            "location_recommendations": location_recommendations[:8],
            "audience_profiles": audience_profiles[:8],
            "product_portfolio": product_portfolio[:8],
            "pricing_strategy": pricing_strategy[:8],
            "customer_experience_plan": customer_experience_plan[:8],
            "technology_plan": technology_plan[:8],
            "financial_assumptions": financial_assumptions[:8],
            "ninety_day_plan": ninety_day_plan[:8],
            "success_metrics": success_metrics[:10],
            "immediate_next_actions": immediate_next_actions[:8],
            "requirement_answers": requirement_answers,
            "dynamic_sections": dynamic_sections,
        },
    }
