"""Expose health, objective, execution, and approval operations as JSON."""

from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from app.services.objective_service import ObjectiveService
from app.services.execution_service import ExecutionService
from app.services.approval_service import ApprovalService
from app.services.dashboard_service import DashboardService
from app.services.readiness_service import ReadinessService
from config.settings import get_settings

api_bp = Blueprint("api", __name__)
objectives = ObjectiveService(); executions = ExecutionService(); approvals = ApprovalService(); dashboard = DashboardService()
readiness = ReadinessService()


@api_bp.get("/health")
def health():
    settings = get_settings()
    return jsonify({
        "status": "ok",
        "mode": "demo-enabled" if settings.enable_demo_data else "live-only",
        "storage": "memory" if settings.use_memory_db or not settings.mongodb_uri else "mongodb",
        "orchestration": {
            "framework": "langgraph",
            "graph": "StateGraph",
            "routing": "conditional",
            "minimum_external_tools": settings.min_external_tools,
        },
        "integrations": {
            "openai": bool(settings.openai_api_key),
            "youtube": bool(settings.youtube_api_key),
            "google_places": bool(settings.google_maps_api_key),
            "firecrawl": bool(settings.firecrawl_api_key),
            "direct_scraper": True,
        },
    })


@api_bp.post("/readiness")
def integration_readiness():
    payload = request.get_json(silent=True) or {}
    try:
        return jsonify(readiness.check(
            live=bool(payload.get("live", False)),
            query=str(payload.get("query", "business customer reviews"))[:300],
            source_url=str(payload.get("source_url", ""))[:2000],
        ))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@api_bp.post("/objectives")
def create_objective():
    try:
        objective = objectives.create(request.get_json(silent=True) or {})
        execution = executions.start(objective["objective_id"], background=True)
        return jsonify({"objective": objective, "execution": execution}), 202
    except (ValidationError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400


@api_bp.get("/objectives")
def list_objectives():
    return jsonify(objectives.list())


@api_bp.get("/executions/<execution_id>")
def execution_status(execution_id: str):
    result = executions.get(execution_id)
    return (jsonify(result), 200) if result else (jsonify({"error": "Not found"}), 404)


@api_bp.post("/executions/<execution_id>/cancel")
def cancel_execution(execution_id: str):
    try:
        return jsonify(executions.request_cancel(execution_id)), 202
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409


@api_bp.get("/executions/<execution_id>/details")
def execution_details(execution_id: str):
    result = dashboard.execution_detail(execution_id)
    return (jsonify(result), 200) if result["execution"] else (jsonify({"error": "Not found"}), 404)


@api_bp.post("/executions/<execution_id>/approval")
def approval(execution_id: str):
    try:
        payload = request.get_json(silent=True) or {}
        approval_record = approvals.apply(execution_id, payload)
        response = {"approval": approval_record, "next_execution": None}
        if payload.get("action") in {"request_analysis", "restart"}:
            execution = executions.executions.get(execution_id)
            response["next_execution"] = executions.start(
                execution["objective_id"],
                background=True,
                human_guidance=payload.get("feedback", ""),
                parent_execution_id=execution_id,
            )
        return jsonify(response)
    except (ValidationError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400
