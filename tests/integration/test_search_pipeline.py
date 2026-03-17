from __future__ import annotations

import os
import tempfile
import unittest

from jobsearch_agent.db.base import BaseStore
from jobsearch_agent.models import JobRecord, SearchRequest
from jobsearch_agent.pipelines.search_graph import run_search_pipeline


class FakeStore(BaseStore):
    def __init__(self) -> None:
        self.search_runs = []

    def upsert_jobs(self, jobs, run):
        return len(jobs)

    def hybrid_search(self, request, embedding):
        return [{"job_id": "job-1"}]

    def fetch_jobs_by_ids(self, ids):
        return [
            JobRecord(
                job_id="job-1",
                source="fixture",
                title="Python AI Engineer",
                company="Example Co",
                canonical_url="https://example.com/job-1",
                description_text="Build agent systems.",
                location="Remote",
                remote_type="remote",
            )
        ]

    def record_search_run(self, run) -> None:
        self.search_runs.append(run)


class SearchPipelineIntegrationTests(unittest.TestCase):
    def test_search_pipeline_exports_results(self) -> None:
        current = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            try:
                store = FakeStore()
                result = run_search_pipeline(store, SearchRequest(query="python"), embedding=[0.0] * 8)
                self.assertEqual(len(result["results"]), 1)
                self.assertTrue(result["export_path"].endswith("output/jobs.csv"))
                self.assertEqual(len(store.search_runs), 2)
                self.assertEqual(store.search_runs[-1].match_count, 1)
                self.assertEqual(store.search_runs[-1].clarified_query, "python")
            finally:
                os.chdir(current)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
