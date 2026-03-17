from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class IngestionRequest:
    sources: list[str] = field(default_factory=list)
    recency_days: int = 7
    force_refresh: bool = False


@dataclass
class SearchRequest:
    query: str
    location: str | None = None
    remote: str | None = None
    company: str | None = None
    recency_days: int = 7
    top_k: int = 25
    analysis: bool = False

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("query must not be empty")
        if self.top_k <= 0:
            raise ValueError("top_k must be positive")
        if self.recency_days <= 0:
            raise ValueError("recency_days must be positive")


@dataclass
class JobRecord:
    job_id: str
    source: str
    title: str
    company: str
    canonical_url: str
    description_text: str
    date_posted: datetime | None = None
    location: str | None = None
    remote_type: str | None = None
    employment_type: str | None = None
    salary_text: str | None = None
    tags: list[str] = field(default_factory=list)
    dedupe_key: str | None = None
    embedding: list[float] = field(default_factory=list)

    def searchable_text(self) -> str:
        return " ".join(
            part for part in [self.title, self.company, self.location, self.description_text] if part
        )


@dataclass
class IngestionRunSummary:
    run_id: str
    started_at: datetime
    completed_at: datetime | None = None
    candidate_count: int = 0
    fetched_count: int = 0
    normalized_count: int = 0
    embedded_count: int = 0
    upserted_count: int = 0
    error_count: int = 0
    airflow_run_id: str | None = None


@dataclass
class SearchRunSummary:
    run_id: str
    query: str
    started_at: datetime
    completed_at: datetime | None = None
    clarified_query: str | None = None
    filters: dict[str, Any] = field(default_factory=dict)
    match_count: int = 0
    export_path: str | None = None
    analysis: dict[str, Any] = field(default_factory=dict)
