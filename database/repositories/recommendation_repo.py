from database.repositories.base_repo import BaseRepository


class RecommendationRepository(BaseRepository):
    collection_name = "recommendations"

    def for_execution(self, execution_id: str):
        return self.list({"execution_id": execution_id})
