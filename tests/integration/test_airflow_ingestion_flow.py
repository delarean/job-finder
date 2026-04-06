from __future__ import annotations

import unittest
from dataclasses import replace

from jobsearch_agent.ingestion.discovery import discover_candidates
from jobsearch_agent.ingestion.embed import embed_records
from jobsearch_agent.ingestion.fetch_extract import fetch_and_extract
from jobsearch_agent.ingestion.normalize import normalize_records
from jobsearch_agent.ingestion.persist import persist_records
from jobsearch_agent.models import IngestionRequest


class RecordingStore:
    def __init__(self) -> None:
        self.ingestion_runs = []
        self.jobs = []

    def record_ingestion_run(self, run) -> None:
        self.ingestion_runs.append(replace(run))

    def upsert_jobs(self, jobs, run) -> int:
        self.jobs.extend(jobs)
        return len(jobs)


class AirflowIngestionFlowTests(unittest.TestCase):
    def test_ingestion_flow_runs_end_to_end_and_records_run_metadata(self) -> None:
        store = RecordingStore()

        candidates = discover_candidates(IngestionRequest(sources=["remoteok", "tavily"]))
        extracted = fetch_and_extract(candidates)
        normalized = normalize_records(extracted)
        embedded = embed_records(normalized)
        summary = persist_records(store, embedded, airflow_run_id="airflow-test-run")

        self.assertGreaterEqual(len(candidates), 2)
        self.assertEqual(len(extracted), len(candidates))
        self.assertEqual(summary.normalized_count, len(normalized))
        self.assertEqual(summary.embedded_count, len(embedded))
        self.assertEqual(summary.upserted_count, len(embedded))
        self.assertEqual(summary.airflow_run_id, "airflow-test-run")
        self.assertEqual(len(store.ingestion_runs), 2)
        self.assertIsNone(store.ingestion_runs[0].completed_at)
        self.assertIsNotNone(store.ingestion_runs[-1].completed_at)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
