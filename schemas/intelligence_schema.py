from pydantic import BaseModel, Field


class IntelligenceItem(BaseModel):
    topic: str
    sentiment: str
    pain_points: list[str] = Field(default_factory=list)
    customer_needs: list[str] = Field(default_factory=list)
    brands: list[str] = Field(default_factory=list)
    purchase_intent: str = "unknown"
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class EvidenceSignal(BaseModel):
    signal: str
    interpretation: str
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class OpportunityInsight(BaseModel):
    opportunity: str
    why_it_matters: str
    recommended_test: str
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class ResearchGap(BaseModel):
    missing_information: str
    decision_impact: str
    next_research_action: str


class LocationCandidate(BaseModel):
    name: str
    address: str = ""
    rating: float | None = None
    user_rating_count: int | None = None
    suitability_reason: str
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class IntelligenceReport(BaseModel):
    summary: str
    items: list[IntelligenceItem]
    trends: list[str] = Field(default_factory=list)
    top_customer_needs: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    target_segments: list[str] = Field(default_factory=list)
    data_sources_used: list[str] = Field(default_factory=list)
    trending_products: list[str] = Field(default_factory=list)
    high_demand_categories: list[str] = Field(default_factory=list)
    overall_sentiment: str = "neutral"
    confidence: float = Field(ge=0, le=1)
    verified_signals: list[EvidenceSignal] = Field(default_factory=list)
    hypotheses: list[EvidenceSignal] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    competitor_signals: list[EvidenceSignal] = Field(default_factory=list)
    location_signals: list[EvidenceSignal] = Field(default_factory=list)
    demand_signals: list[EvidenceSignal] = Field(default_factory=list)
    opportunity_insights: list[OpportunityInsight] = Field(default_factory=list)
    key_risks: list[str] = Field(default_factory=list)
    research_gaps: list[ResearchGap] = Field(default_factory=list)
    next_best_research_actions: list[str] = Field(default_factory=list)
    decision_readiness: str = "low"
    location_candidates: list[LocationCandidate] = Field(default_factory=list)
