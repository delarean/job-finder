from __future__ import annotations

import unittest
from unittest.mock import patch

from jobsearch_agent.ingestion.discovery import discover_candidates
from jobsearch_agent.models import IngestionRequest


class PartialFailureTests(unittest.TestCase):
    def test_discovery_keeps_successful_sources_when_tavily_fails(self) -> None:
        with patch("jobsearch_agent.ingestion.discovery.discover_with_tavily", side_effect=RuntimeError("boom")):
            results = discover_candidates(IngestionRequest(sources=["remoteok", "tavily"]))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["source"], "remoteok")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
