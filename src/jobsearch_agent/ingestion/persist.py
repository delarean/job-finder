from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from jobsearch_agent.db.base import BaseStore
from jobsearch_agent.models import IngestionRunSummary, JobRecord


def persist_records(store: BaseStore, records: list[JobRecord], airflow_run_id: str | None = None) -> IngestionRunSummary:
    summary = IngestionRunSummary(
        run_id=str(uuid4()),
        started_at=datetime.now(UTC),
        airflow_run_id=airflow_run_id,
        normalized_count=len(records),
        embedded_count=sum(1 for record in records if record.embedding),
    )
    store.record_ingestion_run(summary)
    summary.upserted_count = store.upsert_jobs(records, summary)
    summary.completed_at = datetime.now(UTC)
    store.record_ingestion_run(summary)
    return summary
