from __future__ import annotations

from jobsearch_agent.db.base import BaseStore
from jobsearch_agent.models import JobRecord


def retrieve_results(store: BaseStore, ranked_rows: list[dict]) -> list[JobRecord]:
    return store.fetch_jobs_by_ids([row["job_id"] for row in ranked_rows])
