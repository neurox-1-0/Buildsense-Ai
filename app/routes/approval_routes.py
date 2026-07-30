"""Handle human approval decisions from the recommendation review page."""

from flask import Blueprint, flash, redirect, request, url_for
from app.services.approval_service import ApprovalService
from app.services.execution_service import ExecutionService

approval_bp = Blueprint("approval", __name__)
approvals = ApprovalService(); executions = ExecutionService()


@approval_bp.post("/<execution_id>")
def decide(execution_id: str):
    try:
        action = request.form.get("action", "")
        feedback = request.form.get("feedback", "")
        approvals.apply(execution_id, {"action": action, "feedback": feedback, "modified_summary": request.form.get("modified_summary") or None})
        flash(f"Recommendation {action} action recorded.", "success")
        if action in {"request_analysis", "restart"}:
            execution = executions.executions.get(execution_id)
            next_execution = executions.start(
                execution["objective_id"],
                background=True,
                human_guidance=feedback,
                parent_execution_id=execution_id,
            )
            flash("A new execution has been started.", "success")
            return redirect(
                url_for(
                    "dashboard.recommendation_review",
                    execution_id=next_execution["execution_id"],
                )
            )
        return redirect(url_for("dashboard.recommendation_review", execution_id=execution_id))
    except Exception as exc:
        flash(str(exc), "danger")
        return redirect(url_for("dashboard.recommendation_review", execution_id=execution_id))
