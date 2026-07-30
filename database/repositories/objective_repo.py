from database.repositories.base_repo import BaseRepository


class ObjectiveRepository(BaseRepository):
    collection_name = "objectives"

    def get(self, objective_id: str):
        return self.get_one({"objective_id": objective_id})
