from __future__ import annotations

from abc import ABC, abstractmethod

from jobsearch_agent.models import IngestionRunSummary, JobRecord, SearchRequest


class BaseStore(ABC):
    @abstractmethod
    def upsert_jobs(self, jobs: list[JobRecord], run: IngestionRunSummary) -> int:
        raise NotImplementedError

    @abstractmethod
    def hybrid_search(self, request: SearchRequest, embedding: list[float]) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def fetch_jobs_by_ids(self, ids: list[str]) -> list[JobRecord]:
        raise NotImplementedError
