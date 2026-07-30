from database.repositories.base_repo import BaseRepository


class ApprovalRepository(BaseRepository):
    collection_name = "approvals"

    def for_execution(self, execution_id: str):
        return self.list({"execution_id": execution_id})
