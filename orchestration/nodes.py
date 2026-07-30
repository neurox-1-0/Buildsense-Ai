"""Implement the decision nodes executed by the autonomous controller."""

import json
from datetime import datetime, timezone

from agents.data_collection_agent.agent import DataCollectionAgent
from agents.intelligence_analysis_agent.agent import IntelligenceAnalysisAgent
from agents.business_strategy_agent.agent import BusinessStrategyAgent
from core.execution_planner import build_execution_plan
from config.settings import get_settings
from database.repositories.execution_repo import ExecutionRepository
from schemas.controller_schema import ControllerDecision
from tools.openai_client import OpenAIClient
from prompts.planner_prompts import PLANNER_SYSTEM_PROMPT

collector = DataCollectionAgent()
analyzer = IntelligenceAnalysisAgent()
strategist = BusinessStrategyAgent()
controller_ai = OpenAIClient()
executions = ExecutionRepository()


def _elapsed_seconds(state: dict) -> float:
    started = state.get("execution_started_at")
    if not started:
        return 0
    try:
        return max(0, (datetime.now(timezone.utc) - datetime.fromisoformat(started)).total_seconds())
    except ValueError:
        return 0


def _ai_choice(state: dict, allowed: list[str], fallback: str, reason: str) -> tuple[str, str, str]:
    fallback_action = "collect" if fallback.startswith("collect:") else fallback
    fallback_tool = fallback.split(":", 1)[1] if fallback.startswith("collect:") else ""
    if not get_settings().enable_ai_controller or not controller_ai.available or len(allowed) <= 1:
        return fallback_action, fallback_tool, reason
    response = controller_ai.json_response(
        PLANNER_SYSTEM_PROMPT,
        json.dumps({
            "objective": state["objective"],
            "observations": {
                "evidence_count": len(state.get("evidence", [])),
                "attempted_tools": state.get("attempted_tools", []),
                "retry_count": state.get("retry_count", 0),
                "analysis_confidence": (state.get("intelligence") or {}).get("confidence"),
                "human_guidance": state.get("human_guidance", ""),
            },
            "allowed_actions": allowed,
        }, ensure_ascii=False),
    )
    try:
        decision = ControllerDecision.model_validate(response)
        if decision.action not in allowed:
            raise ValueError("AI selected an action outside its capability boundary")
        if decision.action.startswith("collect:"):
            return "collect", decision.action.split(":", 1)[1], decision.reason
        return decision.action, "", decision.reason
    except Exception:
        return fallback_action, fallback_tool, reason


def controller_node(state: dict) -> dict:
    """Inspect observations and choose exactly one next action.

    This is the agentic control loop. No worker node decides what follows it;
    every result returns here for a fresh decision.
    """
    settings = get_settings()
    plan = build_execution_plan(
        state["objective"],
        retry_count=state.get("retry_count", 0),
        guidance=state.get("human_guidance", ""),
    )
    attempted = state.get("attempted_tools", [])
    available_tools = plan["preferred_tools"]
    remaining_tools = [tool for tool in available_tools if tool not in attempted]
    required_tool_attempts = min(settings.min_external_tools, len(available_tools))
    distinct_attempted_tools = len(set(attempted))
    evidence_count = len(state.get("evidence", []))
    intelligence = state.get("intelligence")
    recommendation = state.get("recommendation")
    execution = executions.get(state.get("execution_id", ""))
    tool_calls = sum(
        len(attempt.get("results", []))
        for attempt in state.get("collection_attempts", [])
    )
    cycle_count = len(state.get("action_history", []))
    elapsed = _elapsed_seconds(state)

    if execution and execution.get("status") == "cancel_requested":
        action = "cancel"
        reason = "The user requested cancellation"
        next_tool = ""
        allowed = ["cancel"]
    elif recommendation:
        action = "human_review"
        reason = "A ranked recommendation is ready for management control"
        next_tool = ""
        allowed = ["human_review"]
    elif (
        cycle_count >= settings.max_controller_cycles
        or tool_calls >= settings.max_tool_calls
        or elapsed >= settings.max_execution_seconds
    ):
        if intelligence:
            action = "strategy"
            reason = "Execution budget reached; generate a bounded recommendation with disclosed confidence"
            allowed = ["strategy"]
        else:
            action = "analyze"
            reason = "Execution budget reached; analyze available evidence without further tool calls"
            allowed = ["analyze"]
        next_tool = ""
    elif intelligence:
        confidence = intelligence.get("confidence", 0)
        if confidence >= settings.min_analysis_confidence:
            action = "strategy"
            reason = f"Analysis confidence {confidence:.2f} meets the strategy threshold"
            next_tool = ""
            allowed = ["strategy"]
        elif state.get("retry_count", 0) < settings.max_graph_retries:
            action = "retry_collection"
            reason = f"Analysis confidence {confidence:.2f} is too low; broaden research"
            next_tool = ""
            allowed = ["retry_collection", "strategy"]
        else:
            action = "strategy"
            reason = "Retry budget is exhausted; provide a low-confidence recommendation for human review"
            next_tool = ""
            allowed = ["strategy"]
    elif remaining_tools and distinct_attempted_tools < required_tool_attempts:
        action = "collect"
        next_tool = remaining_tools[0]
        reason = (
            f"Use a distinct evidence tool before analysis "
            f"({distinct_attempted_tools}/{required_tool_attempts} attempted)"
        )
        allowed = [f"collect:{tool}" for tool in remaining_tools]
    elif evidence_count >= settings.min_evidence_items:
        action = "analyze"
        reason = f"{evidence_count} validated records meet the evidence threshold"
        next_tool = ""
        allowed = ["analyze", *[f"collect:{tool}" for tool in remaining_tools]]
    elif remaining_tools:
        action = "collect"
        next_tool = remaining_tools[0]
        reason = plan["tool_rationale"].get(next_tool, "Gather additional external evidence")
        allowed = [f"collect:{tool}" for tool in remaining_tools]
    elif state.get("retry_count", 0) < settings.max_graph_retries and available_tools:
        action = "retry_collection"
        reason = "All selected tools were observed without enough evidence; change the search approach"
        next_tool = ""
        allowed = ["retry_collection", "analyze"] if evidence_count else ["retry_collection"]
    else:
        action = "analyze"
        reason = (
            "No unused live tool is available; analyze the collected evidence and expose the limitation"
        )
        next_tool = ""
        allowed = ["analyze"]

    fallback_action = f"collect:{next_tool}" if action == "collect" else action
    action, ai_tool, reason = _ai_choice(state, allowed, fallback_action, reason)
    if action == "collect":
        next_tool = ai_tool or next_tool

    decision = {
        "cycle": len(state.get("action_history", [])) + 1,
        "action": action,
        "tool": next_tool or None,
        "reason": reason,
        "observations": {
            "evidence_count": evidence_count,
            "attempted_tools": attempted,
            "distinct_tool_attempts": distinct_attempted_tools,
            "required_tool_attempts": required_tool_attempts,
            "retry_count": state.get("retry_count", 0),
            "analysis_confidence": intelligence.get("confidence") if intelligence else None,
            "recommendation_ready": bool(recommendation),
            "tool_calls": tool_calls,
            "elapsed_seconds": round(elapsed, 2),
            "allowed_actions": allowed,
        },
    }
    return {
        "execution_plan": plan,
        "next_action": action,
        "next_tool": next_tool,
        "action_history": state.get("action_history", []) + [decision],
        "status": "deciding",
        "trace_events": state.get("trace_events", []) + [{
            "step": "controller_decision",
            "message": f"Agent chose {action}: {reason}",
            "data": {**decision, "plan": plan},
        }],
    }


def cancel_node(state: dict) -> dict:
    return {
        "status": "cancelled",
        "trace_events": state.get("trace_events", []) + [{
            "step": "cancelled",
            "message": "Execution stopped by user request",
            "data": {"cycle": len(state.get("action_history", []))},
        }],
    }


def collect_node(state: dict) -> dict:
    plan = dict(state["execution_plan"])
    selected_tool = state["next_tool"]
    plan["preferred_tools"] = [selected_tool]
    result = collector.run(state["objective"], plan)
    existing = state.get("evidence", [])
    combined = {item["item_id"]: item for item in existing + result["items"]}
    attempt = {
        "attempt": plan["attempt"],
        "query": plan["query"],
        "tools": plan["preferred_tools"],
        "tool_rationale": plan["tool_rationale"],
        "results": result["tool_results"],
        "errors": result["errors"],
        "accepted_items": len(result["items"]),
    }
    events = state.get("trace_events", []) + result["trace_events"]
    return {
        "execution_plan": plan,
        "attempted_tools": state.get("attempted_tools", []) + [selected_tool],
        "evidence": list(combined.values()),
        "source_errors": state.get("source_errors", []) + result["errors"],
        "collection_attempts": state.get("collection_attempts", []) + [attempt],
        "trace_events": events,
        "status": "collecting",
    }


def retry_collection_node(state: dict) -> dict:
    retry_count = state.get("retry_count", 0) + 1
    reason = (
        "Evidence volume was below the required threshold"
        if len(state.get("evidence", [])) < state.get("execution_plan", {}).get("minimum_evidence", 0)
        else "Analysis confidence was below the required threshold"
    )
    return {
        "retry_count": retry_count,
        "attempted_tools": [],
        "intelligence": None,
        "status": "retrying_collection",
        "trace_events": state.get("trace_events", []) + [{
            "step": "adaptation",
            "message": f"Changed collection approach for attempt {retry_count + 1}",
            "data": {"reason": reason, "next_query_variant": retry_count},
        }],
    }


def analyze_node(state: dict) -> dict:
    intelligence = analyzer.run(state["objective"], state.get("evidence", []))
    return {
        "intelligence": intelligence,
        "status": "analyzing",
        "trace_events": state.get("trace_events", []) + [{
            "step": "analysis",
            "message": intelligence["summary"],
            "data": {
                "engine": intelligence.get("analysis_engine"),
                "confidence": intelligence["confidence"],
                "decision_readiness": intelligence.get("decision_readiness"),
                "evidence_count": len(state.get("evidence", [])),
                "trends": intelligence.get("trends", []),
                "verified_signal_count": len(intelligence.get("verified_signals", [])),
                "opportunity_count": len(intelligence.get("opportunity_insights", [])),
                "research_gaps": intelligence.get("research_gaps", []),
            },
        }],
    }


def strategy_node(state: dict) -> dict:
    plan = state.get("execution_plan", {})
    recommendation = strategist.run(
        state["objective"],
        state["intelligence"],
        constraints={
            "required_constraints": plan.get("required_constraints", []),
            "prohibited_constraints": plan.get("prohibited_constraints", []),
        },
    )
    ranked = [recommendation["recommended_strategy"], *recommendation.get("alternatives", [])]
    return {
        "recommendation": recommendation,
        "status": "strategizing",
        "trace_events": state.get("trace_events", []) + [{
            "step": "decision",
            "message": f"Selected {recommendation['recommended_strategy']['title']} as the highest-ranked strategy",
            "data": {
                "engine": recommendation.get("strategy_engine"),
                "comparison": [
                    {"title": item["title"], "score": item["score"], "risk": item["risk"]}
                    for item in ranked
                ],
                "justification": recommendation["recommended_strategy"]["justification"],
            },
        }],
    }
