"""Provide shared persistence operations for all repository classes."""

from datetime import datetime, timezone
from copy import deepcopy
from typing import Any
from bson import ObjectId
from database.connection import get_database


class BaseRepository:
    """Wrap collection CRUD and remove database-only metadata from results."""
    collection_name = "base"

    @property
    def collection(self):
        return get_database()[self.collection_name]

    @classmethod
    def _clean_document(cls, value):
        """Keep MongoDB implementation details out of application state."""
        if isinstance(value, dict):
            return {
                key: cls._clean_document(item)
                for key, item in value.items()
                if key != "_id"
            }
        if isinstance(value, list):
            return [cls._clean_document(item) for item in value]
        if isinstance(value, ObjectId):
            return str(value)
        return value

    def create(self, document: dict[str, Any]) -> dict[str, Any]:
        clean = self._clean_document(deepcopy(document))
        # PyMongo adds `_id` to the object passed to insert_one. Insert a copy so
        # database metadata cannot mutate application state.
        self.collection.insert_one(deepcopy(clean))
        return clean

    def get_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        document = self.collection.find_one(query)
        return self._clean_document(document) if document else None

    def list(self, query: dict[str, Any] | None = None, limit: int = 100) -> list[dict[str, Any]]:
        return [
            self._clean_document(document)
            for document in self.collection.find(query or {}).sort("created_at", -1).limit(limit)
        ]

    def update(self, query: dict[str, Any], values: dict[str, Any]) -> dict[str, Any] | None:
        values["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.collection.update_one(query, {"$set": values}, upsert=False)
        return self.get_one(query)

    def delete(self, query: dict[str, Any]) -> int:
        """Delete all matching documents and return the number removed."""
        return self.collection.delete_many(query).deleted_count
