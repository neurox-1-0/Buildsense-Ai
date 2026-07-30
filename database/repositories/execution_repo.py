from database.repositories.base_repo import BaseRepository


class ExecutionRepository(BaseRepository):
    collection_name = "executions"

    def get(self, execution_id: str):
        return self.get_one({"execution_id": execution_id})
