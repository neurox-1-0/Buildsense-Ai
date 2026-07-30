from config.settings import get_settings


def _extract_constraints(guidance: str) -> tuple[list[str], list[str]]:
    required = []
    prohibited = []
    for fragment in guidance.replace("\n", ".").split("."):
        text = fragment.strip()
        if not text:
            continue
        lower = text.lower()
        if any(marker in lower for marker in ("do not", "don't", "avoid", "exclude", "must not")):
            prohibited.append(text)
        else:
            required.append(text)
    return required[:10], prohibited[:10]


def build_execution_plan(objective: dict, retry_count: int = 0, guidance: str = "") -> dict:
    settings = get_settings()
    urls = objective.get("source_urls") or []
    keywords = objective.get("keywords") or objective["title"].split()
    base_query = " ".join(keywords)
    context = " ".join(
        part for part in [
            objective.get("industry", ""),
            objective.get("target_market", ""),
            guidance,
        ] if part
    )
    query_variants = [
        base_query,
        f"{base_query} {context}".strip(),
        f"{base_query} customer problems alternatives pricing reviews {context}".strip(),
    ]

    objective_text = " ".join([
        objective.get("title", ""),
        objective.get("description", ""),
        objective.get("industry", ""),
        objective.get("target_market", ""),
        " ".join(keywords),
    ]).lower()
    location_intent = any(
        term in objective_text
        for term in ("location", "where", "area", "city", "place to open", "suitable place")
    )
    if location_intent:
        place_context = " ".join(
            part for part in [
                objective.get("industry", ""),
                objective.get("target_market", ""),
                "competitors reviews",
            ] if part
        )
        query_variants[0] = f"{base_query} {place_context}".strip()
    candidates = []
    if settings.youtube_api_key:
        score = 3 if any(term in objective_text for term in ("review", "customer", "opinion", "product", "video")) else 1
        candidates.append((score, "youtube", "Find public customer discussions and purchase signals"))
    if settings.google_maps_api_key:
        score = 3 if any(term in objective_text for term in ("local", "store", "restaurant", "hotel", "location", "service", "retail")) else 0
        candidates.append((score, "google_places", "Find location-based customer reviews and service complaints"))
    if urls:
        score = 4 if any(term in objective_text for term in ("supplier", "certification", "competitor", "article", "report")) else 2
        candidates.append((score, "scraper", "Read the user-supplied public source pages"))
        if settings.firecrawl_api_key:
            candidates.append((score + 1, "firecrawl", "Extract structured content from supplied pages"))

    # On later attempts use every available source. Initially prefer the smallest
    # useful set so the decision is visible and tied to the objective.
    candidates.sort(key=lambda item: item[0], reverse=True)
    selected = candidates if retry_count else candidates[:3]
    tools = [name for _, name, _ in selected]
    rationale = {name: f"{reason} (relevance score {score})" for score, name, reason in selected}
    if not tools:
        rationale["none"] = "No live integration is configured and no public source URL was supplied"

    required_constraints, prohibited_constraints = _extract_constraints(guidance)
    return {
        "objective_summary": objective["description"],
        "keywords": keywords,
        "query": query_variants[min(retry_count, len(query_variants) - 1)],
        "query_variants": query_variants,
        "preferred_tools": tools,
        "tool_rationale": rationale,
        "attempt": retry_count + 1,
        "human_guidance": guidance,
        "required_constraints": required_constraints,
        "prohibited_constraints": prohibited_constraints,
        "minimum_evidence": settings.min_evidence_items,
        "maximum_retries": settings.max_graph_retries,
    }
