from database.repositories.base_repo import BaseRepository


class IntelligenceRepository(BaseRepository):
    collection_name = "intelligence"

    def for_execution(self, execution_id: str):
        return self.list({"execution_id": execution_id})
