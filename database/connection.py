"""Provide MongoDB access and a test-friendly in-memory substitute."""

import logging
from copy import deepcopy
from threading import RLock
from typing import Any
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from config.settings import get_settings

logger = logging.getLogger(__name__)


class MemoryCollection:
    """Implement the MongoDB collection operations required by local tests."""
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.lock = RLock()

    @staticmethod
    def _match(row: dict, query: dict) -> bool:
        return all(row.get(key) == value for key, value in query.items())

    def insert_one(self, document: dict):
        with self.lock:
            self.rows.append(deepcopy(document))
        return type("InsertResult", (), {"inserted_id": document.get("_id")})()

    def insert_many(self, documents: list[dict]):
        with self.lock:
            self.rows.extend(deepcopy(documents))
        return type("InsertManyResult", (), {"inserted_ids": [d.get("_id") for d in documents]})()

    def find_one(self, query: dict):
        with self.lock:
            for row in reversed(self.rows):
                if self._match(row, query):
                    return deepcopy(row)
        return None

    def find(self, query: dict | None = None):
        query = query or {}
        with self.lock:
            result = [deepcopy(r) for r in self.rows if self._match(r, query)]
        return MemoryCursor(result)

    def update_one(self, query: dict, update: dict, upsert: bool = False):
        with self.lock:
            for row in self.rows:
                if self._match(row, query):
                    row.update(deepcopy(update.get("$set", {})))
                    return type("UpdateResult", (), {"matched_count": 1})()
            if upsert:
                new_row = {**query, **deepcopy(update.get("$set", {}))}
                self.rows.append(new_row)
        return type("UpdateResult", (), {"matched_count": 0})()

    def delete_many(self, query: dict):
        with self.lock:
            before = len(self.rows)
            self.rows = [r for r in self.rows if not self._match(r, query)]
        return type("DeleteResult", (), {"deleted_count": before - len(self.rows)})()


class MemoryCursor(list):
    def sort(self, key: str, direction: int):
        return MemoryCursor(sorted(self, key=lambda x: x.get(key, ""), reverse=direction < 0))

    def limit(self, n: int):
        return MemoryCursor(self[:n])


class MemoryDatabase:
    def __init__(self) -> None:
        self.collections: dict[str, MemoryCollection] = {}

    def __getitem__(self, name: str) -> MemoryCollection:
        self.collections.setdefault(name, MemoryCollection())
        return self.collections[name]


_memory_db = MemoryDatabase()
_client: MongoClient | None = None


def get_database():
    global _client
    settings = get_settings()
    if settings.use_memory_db or not settings.mongodb_uri:
        return _memory_db
    try:
        if _client is None:
            _client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
            _client.admin.command("ping")
        return _client[settings.mongodb_database]
    except PyMongoError as exc:
        logger.warning("MongoDB unavailable; using memory database: %s", exc)
        return _memory_db


def reset_memory_database() -> None:
    global _memory_db
    _memory_db = MemoryDatabase()
