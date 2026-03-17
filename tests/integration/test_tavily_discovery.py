from __future__ import annotations

import unittest
from unittest.mock import patch

from jobsearch_agent.ingestion.discovery import discover_candidates
from jobsearch_agent.models import IngestionRequest


class TavilyDiscoveryTests(unittest.TestCase):
    def test_tavily_discovery_is_included_when_available(self) -> None:
        results = discover_candidates(IngestionRequest(sources=["tavily"]))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["source"], "tavily")

    def test_tavily_failure_is_captured_as_empty_result(self) -> None:
        with patch("jobsearch_agent.ingestion.discovery.discover_with_tavily", side_effect=RuntimeError("boom")):
            results = discover_candidates(IngestionRequest(sources=["tavily"]))

        self.assertEqual(results, [])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
