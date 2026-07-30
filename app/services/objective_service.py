"""Validate business objectives and manage their stored lifecycle."""

from schemas.objective_schema import ObjectiveCreate
from core.utils import new_id
from database.models.objective_model import objective_document
from database.repositories.objective_repo import ObjectiveRepository
from database.repositories.execution_repo import ExecutionRepository
from database.repositories.raw_data_repo import RawDataRepository
from database.repositories.intelligence_repo import IntelligenceRepository
from database.repositories.recommendation_repo import RecommendationRepository
from database.repositories.decision_trail_repo import DecisionTrailRepository
from database.repositories.approval_repo import ApprovalRepository


class ObjectiveService:
    """Coordinate objective creation, lookup, listing, and safe deletion."""
    def __init__(self) -> None:
        self.repo = ObjectiveRepository()
        self.executions = ExecutionRepository()
        self.related_repositories = (
            RawDataRepository(),
            IntelligenceRepository(),
            RecommendationRepository(),
            DecisionTrailRepository(),
            ApprovalRepository(),
        )

    def create(self, payload: dict) -> dict:
        data = ObjectiveCreate.model_validate(payload).model_dump()
        return self.repo.create(objective_document(new_id("OBJ"), data))

    def get(self, objective_id: str):
        return self.repo.get(objective_id)

    def list(self):
        return self.repo.list(limit=100)

    def delete(self, objective_id: str) -> dict:
        """Remove a non-running objective and its execution-linked child data."""
        objective = self.get(objective_id)
        if not objective:
            raise ValueError("Business opportunity not found.")
        execution_rows = self.executions.list(
            {"objective_id": objective_id}, limit=250
        )
        if any(
            row.get("status") in {"queued", "running", "cancel_requested"}
            for row in execution_rows
        ):
            raise ValueError(
                "An active analysis cannot be deleted. Stop it and wait for "
                "the workflow to finish first."
            )
        removed = 0
        # Execution IDs are the reliable relationship key for every child
        # collection, including older decision-trail records.
        for execution in execution_rows:
            for repository in self.related_repositories:
                removed += repository.delete(
                    {"execution_id": execution["execution_id"]}
                )
        removed += self.executions.delete({"objective_id": objective_id})
        removed += self.repo.delete({"objective_id": objective_id})
        return {"objective": objective, "removed": removed}
