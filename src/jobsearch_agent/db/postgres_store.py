from __future__ import annotations

from dataclasses import asdict
from typing import Any

from jobsearch_agent.db.base import BaseStore
from jobsearch_agent.db.query_builder import build_hybrid_query, build_hybrid_sql
from jobsearch_agent.models import IngestionRunSummary, JobRecord, SearchRequest


class PostgresStore(BaseStore):
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    def _connect(self):
        try:
            import psycopg
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("psycopg is required to connect to PostgreSQL") from exc
        return psycopg.connect(self.dsn)

    def upsert_jobs(self, jobs: list[JobRecord], run: IngestionRunSummary) -> int:
        if not jobs:
            return 0
        payloads = [self._job_payload(job, run) for job in jobs]
        sql = """
        INSERT INTO job_records (
            job_id, source, title, company, canonical_url, description_text,
            date_posted, location, remote_type, employment_type, salary_text,
            tags, dedupe_key, embedding, fts_document, date_ingested
        )
        VALUES (
            %(job_id)s, %(source)s, %(title)s, %(company)s, %(canonical_url)s, %(description_text)s,
            %(date_posted)s, %(location)s, %(remote_type)s, %(employment_type)s, %(salary_text)s,
            %(tags)s, %(dedupe_key)s, %(embedding)s,
            to_tsvector('english', %(search_text)s),
            NOW()
        )
        ON CONFLICT (dedupe_key) DO UPDATE SET
            title = EXCLUDED.title,
            company = EXCLUDED.company,
            description_text = EXCLUDED.description_text,
            date_posted = EXCLUDED.date_posted,
            location = EXCLUDED.location,
            remote_type = EXCLUDED.remote_type,
            employment_type = EXCLUDED.employment_type,
            salary_text = EXCLUDED.salary_text,
            tags = EXCLUDED.tags,
            embedding = EXCLUDED.embedding,
            fts_document = EXCLUDED.fts_document,
            date_ingested = NOW()
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.executemany(sql, payloads)
            conn.commit()
        return len(payloads)

    def hybrid_search(self, request: SearchRequest, embedding: list[float]) -> list[dict[str, Any]]:
        query = build_hybrid_query(request)
        params = {
            "lexical_query": query.lexical_query or request.query,
            "embedding": embedding,
            "location": query.filters.get("location"),
            "remote_type": query.filters.get("remote_type"),
            "company": query.filters.get("company"),
            "posted_after": query.filters["posted_after"],
            "top_k": query.top_k,
        }
        with self._connect() as conn:
            with conn.cursor(row_factory=dict_row_factory) as cur:
                cur.execute(build_hybrid_sql(query), params)
                return list(cur.fetchall())

    def fetch_jobs_by_ids(self, ids: list[str]) -> list[JobRecord]:
        if not ids:
            return []
        sql = """
        SELECT job_id, source, title, company, canonical_url, description_text,
               date_posted, location, remote_type, employment_type, salary_text,
               tags, dedupe_key
        FROM job_records
        WHERE job_id = ANY(%(ids)s)
        """
        with self._connect() as conn:
            with conn.cursor(row_factory=dict_row_factory) as cur:
                cur.execute(sql, {"ids": ids})
                rows = cur.fetchall()
        return [JobRecord(**row) for row in rows]

    @staticmethod
    def _job_payload(job: JobRecord, run: IngestionRunSummary) -> dict[str, Any]:
        payload = asdict(job)
        payload["search_text"] = job.searchable_text()
        payload["run_id"] = run.run_id
        return payload


def dict_row_factory(cursor):
    columns = [col.name for col in cursor.description]

    def factory(row):
        return {columns[index]: value for index, value in enumerate(row)}

    return factory
