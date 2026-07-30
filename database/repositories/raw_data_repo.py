from database.repositories.base_repo import BaseRepository


class RawDataRepository(BaseRepository):
    collection_name = "raw_data"

    def for_execution(self, execution_id: str):
        return self.list({"execution_id": execution_id})
