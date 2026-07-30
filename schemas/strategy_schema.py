from pydantic import BaseModel, Field


class StrategyCandidate(BaseModel):
    title: str
    description: str
    expected_impact: str
    implementation_cost: str
    risk: str
    score: float = Field(ge=0, le=100)
    justification: str
    evidence_ids: list[str] = Field(default_factory=list)


class RequirementAnswer(BaseModel):
    requirement: str
    recommendation: str
    rationale: str
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    validation_needed: str = ""


class DynamicReportSection(BaseModel):
    title: str
    purpose: str
    recommendations: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    success_measure: str = ""


class FinalBusinessReport(BaseModel):
    business_goal: str
    opportunity_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=100)
    data_sources_used: list[str] = Field(default_factory=list)
    top_customer_complaints: list[str] = Field(default_factory=list)
    trending_products: list[str] = Field(default_factory=list)
    high_demand_categories: list[str] = Field(default_factory=list)
    recommended_business_changes: list[str] = Field(default_factory=list)
    marketing_recommendations: list[str] = Field(default_factory=list)
    operational_improvements: list[str] = Field(default_factory=list)
    overall_recommendation: str
    target_markets: list[str] = Field(default_factory=list)
    top_customer_needs: list[str] = Field(default_factory=list)
    competitive_advantages: list[str] = Field(default_factory=list)
    recommended_launch_strategy: list[str] = Field(default_factory=list)
    key_risks: list[str] = Field(default_factory=list)
    location_recommendations: list[str] = Field(default_factory=list)
    audience_profiles: list[str] = Field(default_factory=list)
    product_portfolio: list[str] = Field(default_factory=list)
    pricing_strategy: list[str] = Field(default_factory=list)
    customer_experience_plan: list[str] = Field(default_factory=list)
    technology_plan: list[str] = Field(default_factory=list)
    financial_assumptions: list[str] = Field(default_factory=list)
    ninety_day_plan: list[str] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)
    immediate_next_actions: list[str] = Field(default_factory=list)
    requirement_answers: list[RequirementAnswer] = Field(default_factory=list)
    dynamic_sections: list[DynamicReportSection] = Field(default_factory=list)


class Recommendation(BaseModel):
    summary: str
    recommended_strategy: StrategyCandidate
    alternatives: list[StrategyCandidate] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    evidence_summary: list[str] = Field(default_factory=list)
    final_business_report: FinalBusinessReport
