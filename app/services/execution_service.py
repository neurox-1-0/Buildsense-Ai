"""Start, monitor, cancel, and persist autonomous analysis executions."""

import logging
from threading import Thread
from flask import current_app
from config.settings import get_settings
from core.utils import new_id, utc_now
from core.decision_trail_logger import DecisionTrailLogger
from database.models.execution_model import execution_document
from database.repositories.execution_repo import ExecutionRepository
from database.repositories.objective_repo import ObjectiveRepository
from database.repositories.raw_data_repo import RawDataRepository
from database.repositories.intelligence_repo import IntelligenceRepository
from database.repositories.recommendation_repo import RecommendationRepository

logger = logging.getLogger(__name__)


class ExecutionService:
    def __init__(self) -> None:
        self.executions = ExecutionRepository()
        self.objectives = ObjectiveRepository()
        self.raw = RawDataRepository()
        self.intelligence = IntelligenceRepository()
        self.recommendations = RecommendationRepository()
        self.trail = DecisionTrailLogger()

    def start(
        self,
        objective_id: str,
        background: bool = True,
        human_guidance: str = "",
        parent_execution_id: str | None = None,
    ) -> dict:
        objective = self.objectives.get(objective_id)
        if not objective:
            raise ValueError("Objective not found")
        execution = self.executions.create(
            execution_document(
                new_id("EXE"),
                objective_id,
                human_guidance=human_guidance,
                parent_execution_id=parent_execution_id,
            )
        )
        self.objectives.update({"objective_id": objective_id}, {"status": "running"})
        graph = current_app.extensions["buildsense_graph"]
        if background:
            app = current_app._get_current_object()
            Thread(target=self._run_with_context, args=(app, graph, execution, objective), daemon=True).start()
        else:
            self._run(graph, execution, objective)
        return execution

    def _run_with_context(self, app, graph, execution, objective):
        with app.app_context():
            self._run(graph, execution, objective)

    def _run(self, graph, execution: dict, objective: dict) -> None:
        execution_id = execution["execution_id"]
        try:
            self.executions.update({"execution_id": execution_id}, {"status": "running", "current_node": "graph"})
            self.trail.log(execution_id, "objective", "Business objective received", {"title": objective["title"]})
            initial_state = {
                "objective_id": objective["objective_id"],
                "execution_id": execution_id,
                "objective": objective,
                "execution_started_at": execution["created_at"],
                "human_guidance": execution.get("human_guidance", ""),
                "retry_count": 0,
                "status": "queued",
                "evidence": [],
                "attempted_tools": [],
                "action_history": [],
                "collection_attempts": [],
                "source_errors": [],
                "trace_events": [],
            }
            # A controller cycle uses two LangGraph steps: controller + worker.
            # Keep the LangGraph recursion guard above the application's own
            # stricter cycle budget so the controller can terminate gracefully.
            recursion_limit = (get_settings().max_controller_cycles * 2) + 10
            state = graph.invoke(
                initial_state,
                {"recursion_limit": recursion_limit},
            )
            if state.get("status") == "cancelled":
                for event in state.get("trace_events", []):
                    self.trail.log(
                        execution_id,
                        event["step"],
                        event["message"],
                        event.get("data", {}),
                    )
                self.executions.update(
                    {"execution_id": execution_id},
                    {"status": "cancelled", "current_node": "cancelled"},
                )
                self.objectives.update(
                    {"objective_id": objective["objective_id"]},
                    {"status": "cancelled"},
                )
                return
            for item in state.get("evidence", []):
                self.raw.create({**item, "execution_id": execution_id, "objective_id": objective["objective_id"], "created_at": utc_now()})
            self.intelligence.create({"intelligence_id": new_id("INT"), "execution_id": execution_id, "objective_id": objective["objective_id"], **state["intelligence"], "created_at": utc_now()})
            self.recommendations.create({"recommendation_id": new_id("REC"), "execution_id": execution_id, "objective_id": objective["objective_id"], "status": "pending", **state["recommendation"], "created_at": utc_now()})
            for event in state.get("trace_events", []):
                self.trail.log(
                    execution_id,
                    event["step"],
                    event["message"],
                    event.get("data", {}),
                )
            attempted_tools = sorted({
                result["tool"]
                for attempt in state.get("collection_attempts", [])
                for result in attempt.get("results", [])
                if result.get("tool")
            })
            productive_tools = sorted({
                result["tool"]
                for attempt in state.get("collection_attempts", [])
                for result in attempt.get("results", [])
                if result.get("status") == "productive"
            })
            demo_data_used = any(
                item.get("metadata", {}).get("is_demo")
                for item in state.get("evidence", [])
            )
            compliance = {
                "goal_directed_autonomy": bool(state.get("action_history")),
                "dynamic_decision_making": len({
                    entry.get("action")
                    for entry in state.get("action_history", [])
                    if entry.get("action")
                }) >= 3,
                "three_external_tools_attempted": (
                    len(attempted_tools) >= get_settings().min_external_tools
                ),
                "three_productive_external_tools": (
                    len(productive_tools) >= get_settings().min_external_tools
                ),
                "human_oversight": state.get("status") == "awaiting_approval",
                "transparent_reasoning": all(
                    entry.get("reason")
                    for entry in state.get("action_history", [])
                ),
                "real_live_evidence": bool(state.get("evidence")) and not demo_data_used,
            }
            self.executions.update(
                {"execution_id": execution_id},
                {
                    "status": "awaiting_approval",
                    "current_node": "human_review",
                    "retry_count": state.get("retry_count", 0),
                    "collection_attempts": state.get("collection_attempts", []),
                    "action_history": state.get("action_history", []),
                    "source_errors": state.get("source_errors", []),
                    "attempted_tools": attempted_tools,
                    "attempted_tool_count": len(attempted_tools),
                    "tools_used": productive_tools,
                    "productive_tool_count": len(productive_tools),
                    "demo_data_used": demo_data_used,
                    "guideline_compliance": compliance,
                },
            )
            self.objectives.update({"objective_id": objective["objective_id"]}, {"status": "awaiting_approval"})
        except Exception as exc:
            logger.exception("Execution failed")
            self.executions.update({"execution_id": execution_id}, {"status": "failed", "current_node": "error", "error": str(exc)})
            self.objectives.update({"objective_id": objective["objective_id"]}, {"status": "failed"})
            self.trail.log(execution_id, "error", "Execution failed", {"error": str(exc)})

    def get(self, execution_id: str) -> dict | None:
        execution = self.executions.get(execution_id)
        if not execution:
            return None
        execution["recommendation"] = next(iter(self.recommendations.for_execution(execution_id)), None)
        execution["intelligence"] = next(iter(self.intelligence.for_execution(execution_id)), None)
        execution["evidence_count"] = len(self.raw.for_execution(execution_id))
        return execution

    def latest_for_objective(self, objective_id: str) -> dict | None:
        rows = self.executions.list({"objective_id": objective_id}, limit=1)
        return rows[0] if rows else None

    def request_cancel(self, execution_id: str) -> dict:
        execution = self.executions.get(execution_id)
        if not execution:
            raise ValueError("Execution not found")
        if execution.get("status") not in {"queued", "running"}:
            raise ValueError(f"Execution cannot be cancelled while {execution.get('status')}")
        return self.executions.update(
            {"execution_id": execution_id},
            {"status": "cancel_requested", "current_node": "cancellation_requested"},
        )
