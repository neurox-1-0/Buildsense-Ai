"""Assemble stored records into view models used by dashboard templates."""

from database.repositories.objective_repo import ObjectiveRepository
from database.repositories.execution_repo import ExecutionRepository
from database.repositories.raw_data_repo import RawDataRepository
from database.repositories.intelligence_repo import IntelligenceRepository
from database.repositories.recommendation_repo import RecommendationRepository
from database.repositories.decision_trail_repo import DecisionTrailRepository
from database.repositories.approval_repo import ApprovalRepository


class DashboardService:
    """Provide portfolio, objective, and execution page summaries."""
    def __init__(self) -> None:
        self.objectives = ObjectiveRepository(); self.executions = ExecutionRepository(); self.raw = RawDataRepository(); self.intelligence = IntelligenceRepository(); self.recommendations = RecommendationRepository(); self.trails = DecisionTrailRepository(); self.approvals = ApprovalRepository()

    @staticmethod
    def _with_compliance(execution: dict | None) -> dict | None:
        """Backfill judge-readiness proof for executions created before the field existed."""
        if not execution or execution.get("guideline_compliance"):
            return execution
        action_history = execution.get("action_history", [])
        collection_attempts = execution.get("collection_attempts", [])
        attempted_tools = sorted({
            result.get("tool")
            for attempt in collection_attempts
            for result in attempt.get("results", [])
            if result.get("tool")
        })
        productive_tools = sorted({
            result.get("tool")
            for attempt in collection_attempts
            for result in attempt.get("results", [])
            if result.get("tool") and result.get("status") == "productive"
        })
        if not attempted_tools:
            attempted_tools = sorted(set(execution.get("attempted_tools", [])))
        if not productive_tools:
            productive_tools = sorted(set(execution.get("tools_used", [])))
        execution["attempted_tools"] = attempted_tools
        execution["attempted_tool_count"] = len(attempted_tools)
        execution["tools_used"] = productive_tools
        execution["productive_tool_count"] = len(productive_tools)
        execution["guideline_compliance"] = {
            "goal_directed_autonomy": bool(action_history),
            "dynamic_decision_making": len({
                entry.get("action")
                for entry in action_history
                if entry.get("action")
            }) >= 3,
            "three_external_tools_attempted": len(attempted_tools) >= 3,
            "three_productive_external_tools": len(productive_tools) >= 3,
            "human_oversight": execution.get("status") in {
                "awaiting_approval",
                "approved",
                "approved_with_modification",
                "rejected",
            },
            "transparent_reasoning": bool(action_history) and all(
                entry.get("reason") for entry in action_history
            ),
            "real_live_evidence": (
                bool(productive_tools) and not execution.get("demo_data_used", False)
            ),
        }
        return execution

    def objective_detail(self, objective_id: str) -> dict:
        objective = self.objectives.get(objective_id)
        executions = [
            self._with_compliance(execution)
            for execution in self.executions.list({"objective_id": objective_id}, limit=20)
        ]
        latest = executions[0] if executions else None
        active_statuses = {"queued", "running", "cancel_requested"}
        return {
            "objective": objective,
            "executions": executions,
            "latest": latest,
            "can_delete": not any(
                execution.get("status") in active_statuses
                for execution in executions
            ),
        }

    def overview(self) -> dict:
        objectives = self.objectives.list(limit=100)
        executions = [
            self._with_compliance(execution)
            for execution in self.executions.list(limit=250)
        ]
        latest_by_objective = {}
        for execution in executions:
            latest_by_objective.setdefault(execution["objective_id"], execution)
        for objective in objectives:
            objective["latest_execution"] = latest_by_objective.get(objective["objective_id"])
        statuses = [execution.get("status") for execution in executions]
        return {
            "objectives": objectives,
            "stats": {
                "objectives": len(objectives),
                "active": sum(status in {"queued", "running", "cancel_requested"} for status in statuses),
                "review": sum(status == "awaiting_approval" for status in statuses),
                "approved": sum(status in {"approved", "approved_with_modification"} for status in statuses),
            },
        }

    def execution_detail(self, execution_id: str) -> dict:
        return {
            "execution": self._with_compliance(self.executions.get(execution_id)),
            "evidence": self.raw.for_execution(execution_id),
            "intelligence": next(iter(self.intelligence.for_execution(execution_id)), None),
            "recommendation": next(iter(self.recommendations.for_execution(execution_id)), None),
            "trail": list(reversed(self.trails.for_execution(execution_id))),
            "approvals": self.approvals.for_execution(execution_id),
        }
