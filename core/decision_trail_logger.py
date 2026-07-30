from core.utils import new_id, utc_now
from database.repositories.decision_trail_repo import DecisionTrailRepository


class DecisionTrailLogger:
    def __init__(self) -> None:
        self.repo = DecisionTrailRepository()

    def log(self, execution_id: str, step: str, message: str, data: dict | None = None) -> dict:
        document = {
            "trail_id": new_id("TRL"),
            "execution_id": execution_id,
            "step": step,
            "message": message,
            "data": data or {},
            "created_at": utc_now(),
        }
        return self.repo.create(document)
