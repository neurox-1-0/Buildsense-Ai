"""Render dashboard pages and handle browser-based objective actions."""

from flask import Blueprint, abort, flash, jsonify, make_response, redirect, render_template, request, url_for
from app.services.objective_service import ObjectiveService
from app.services.execution_service import ExecutionService
from app.services.dashboard_service import DashboardService
from app.services.pdf_report_service import PDFReportService

dashboard_bp = Blueprint("dashboard", __name__)
objectives = ObjectiveService(); executions = ExecutionService(); dashboard = DashboardService()


@dashboard_bp.get("/")
def index():
    return render_template("dashboard.html", **dashboard.overview())


@dashboard_bp.post("/objectives")
def create_objective():
    try:
        payload = {"title": request.form.get("title", ""), "description": request.form.get("description", ""), "industry": request.form.get("industry", "General business"), "target_market": request.form.get("target_market", "Local customers"), "keywords": [k.strip() for k in request.form.get("keywords", "").split(",") if k.strip()], "source_urls": [u.strip() for u in request.form.get("source_urls", "").splitlines() if u.strip()]}
        objective = objectives.create(payload)
        execution = executions.start(objective["objective_id"], background=True)
        flash("Objective created and execution started.", "success")
        return redirect(url_for("dashboard.objective_detail", objective_id=objective["objective_id"]))
    except Exception as exc:
        flash(str(exc), "danger")
        return redirect(url_for("dashboard.index"))


@dashboard_bp.get("/objectives/<objective_id>")
def objective_detail(objective_id: str):
    data = dashboard.objective_detail(objective_id)
    if not data["objective"]: abort(404)
    return render_template("objective_detail.html", **data)


@dashboard_bp.post("/objectives/<objective_id>/delete")
def delete_objective(objective_id: str):
    try:
        result = objectives.delete(objective_id)
        flash(
            f'"{result["objective"]["title"]}" and all related records were deleted.',
            "success",
        )
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("dashboard.index"))


@dashboard_bp.get("/executions/<execution_id>/trail")
def decision_trail(execution_id: str):
    data = dashboard.execution_detail(execution_id)
    if not data["execution"]: abort(404)
    return render_template("decision_trail.html", **data)


@dashboard_bp.get("/executions/<execution_id>/review")
def recommendation_review(execution_id: str):
    data = dashboard.execution_detail(execution_id)
    if not data["execution"]: abort(404)
    return render_template("recommendation_review.html", **data)


@dashboard_bp.post("/executions/<execution_id>/cancel")
def cancel_execution(execution_id: str):
    try:
        execution = executions.request_cancel(execution_id)
        flash("Cancellation requested. The controller will stop at the next decision point.", "warning")
        return redirect(
            url_for("dashboard.objective_detail", objective_id=execution["objective_id"])
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(request.referrer or url_for("dashboard.index"))


@dashboard_bp.get("/executions/<execution_id>/report")
def approved_report(execution_id: str):
    data = dashboard.execution_detail(execution_id)
    execution = data["execution"]
    if not execution:
        abort(404)
    if execution.get("status") not in {"approved", "approved_with_modification"}:
        abort(409, description="The report is available after management approval")
    payload = {
        "objective_id": execution["objective_id"],
        "execution": execution,
        "intelligence": data["intelligence"],
        "recommendation": data["recommendation"],
        "evidence": data["evidence"],
        "decision_trail": data["trail"],
        "approvals": data["approvals"],
    }
    response = jsonify(payload)
    response.headers["Content-Disposition"] = (
        f'attachment; filename="buildsense-{execution_id}-approved-report.json"'
    )
    return response


@dashboard_bp.get("/executions/<execution_id>/report.pdf")
def approved_pdf_report(execution_id: str):
    data = dashboard.execution_detail(execution_id)
    execution = data["execution"]
    if not execution:
        abort(404)
    if execution.get("status") not in {"approved", "approved_with_modification"}:
        abort(409, description="The PDF report is available after management approval")
    objective = objectives.get(execution["objective_id"])
    pdf = PDFReportService().build({**data, "objective": objective})
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f'attachment; filename="buildsense-{execution_id}-approved-report.pdf"'
    )
    return response
