from database.repositories.base_repo import BaseRepository


class DecisionTrailRepository(BaseRepository):
    collection_name = "decision_trails"

    def for_execution(self, execution_id: str):
        return self.list({"execution_id": execution_id})
