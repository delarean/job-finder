from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    postgres_dsn: str = os.getenv(
        "JOBSEARCH_POSTGRES_DSN",
        "postgresql://jobsearch:jobsearch@localhost:5432/jobsearch",
    )
    recency_days: int = int(os.getenv("JOBSEARCH_RECENCY_DAYS", "7"))
    top_k: int = int(os.getenv("JOBSEARCH_TOP_K", "25"))
    tavily_api_key: str = os.getenv("JOBSEARCH_TAVILY_API_KEY", "")
    embedding_model: str = os.getenv(
        "JOBSEARCH_EMBEDDING_MODEL",
        "text-embedding-3-small",
    )
    airflow_schedule: str = os.getenv("JOBSEARCH_AIRFLOW_SCHEDULE", "0 */6 * * *")


def get_settings() -> Settings:
    return Settings()
