from core.utils import new_id, utc_now
"""Validate and apply the manager's final recommendation decision."""

from schemas.approval_schema import ApprovalRequest
from database.repositories.approval_repo import ApprovalRepository
from database.repositories.execution_repo import ExecutionRepository
from database.repositories.objective_repo import ObjectiveRepository
from database.repositories.recommendation_repo import RecommendationRepository
from core.decision_trail_logger import DecisionTrailLogger


class ApprovalService:
    def __init__(self) -> None:
        self.approvals = ApprovalRepository()
        self.executions = ExecutionRepository()
        self.objectives = ObjectiveRepository()
        self.recommendations = RecommendationRepository()
        self.trail = DecisionTrailLogger()

    def apply(self, execution_id: str, payload: dict) -> dict:
        request = ApprovalRequest.model_validate(payload)
        execution = self.executions.get(execution_id)
        if not execution:
            raise ValueError("Execution not found")
        if execution.get("status") != "awaiting_approval":
            raise ValueError(
                f"Execution cannot be reviewed while its status is {execution.get('status')}"
            )
        status_map = {"approve": "approved", "reject": "rejected", "modify": "approved_with_modification", "request_analysis": "analysis_requested", "restart": "restart_requested"}
        status = status_map[request.action]
        approval = self.approvals.create({"approval_id": new_id("APR"), "execution_id": execution_id, "objective_id": execution["objective_id"], "action": request.action, "feedback": request.feedback, "modified_summary": request.modified_summary, "created_at": utc_now()})
        self.executions.update({"execution_id": execution_id}, {"status": status, "current_node": "human_decision"})
        self.objectives.update({"objective_id": execution["objective_id"]}, {"status": status})
        recommendations = self.recommendations.for_execution(execution_id)
        if recommendations:
            values = {"status": status}
            if request.modified_summary:
                values["summary"] = request.modified_summary
            self.recommendations.update({"recommendation_id": recommendations[0]["recommendation_id"]}, values)
        self.trail.log(execution_id, "human_decision", f"Manager action: {request.action}", {"feedback": request.feedback})
        return approval
