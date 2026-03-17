from __future__ import annotations

from abc import ABC, abstractmethod

from jobsearch_agent.models import IngestionRunSummary, JobRecord, SearchRequest, SearchRunSummary


class BaseStore(ABC):
    def initialize_schema(self) -> None:
        """Initialize storage schema when supported."""

    @abstractmethod
    def upsert_jobs(self, jobs: list[JobRecord], run: IngestionRunSummary) -> int:
        raise NotImplementedError

    @abstractmethod
    def hybrid_search(self, request: SearchRequest, embedding: list[float]) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def fetch_jobs_by_ids(self, ids: list[str]) -> list[JobRecord]:
        raise NotImplementedError

    def record_ingestion_run(self, run: IngestionRunSummary) -> None:
        """Persist ingestion run metadata when supported."""

    def record_search_run(self, run: SearchRunSummary) -> None:
        """Persist search run metadata when supported."""
