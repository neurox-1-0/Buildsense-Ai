from typing import Any, TypedDict


class BuildSenseState(TypedDict, total=False):
    objective_id: str
    execution_id: str
    objective: dict[str, Any]
    execution_plan: dict[str, Any]
    human_guidance: str
    next_action: str
    next_tool: str
    attempted_tools: list[str]
    action_history: list[dict[str, Any]]
    execution_started_at: str
    evidence: list[dict[str, Any]]
    source_errors: list[dict[str, Any]]
    collection_attempts: list[dict[str, Any]]
    trace_events: list[dict[str, Any]]
    intelligence: dict[str, Any]
    recommendation: dict[str, Any]
    retry_count: int
    status: str
    awaiting_human: bool
    human_action: str
    human_feedback: str
    error: str | None
