from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from jobsearch_agent.db.query_builder import build_hybrid_query
from jobsearch_agent.models import SearchRequest


class RecencyTests(unittest.TestCase):
    def test_build_hybrid_query_sets_posted_after_boundary(self) -> None:
        before = datetime.now(timezone.utc) - timedelta(days=7, seconds=5)
        query = build_hybrid_query(SearchRequest(query="python", recency_days=7))
        after = datetime.now(timezone.utc) - timedelta(days=7) + timedelta(seconds=5)

        posted_after = datetime.fromisoformat(query.filters["posted_after"])
        self.assertGreaterEqual(posted_after, before)
        self.assertLessEqual(posted_after, after)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
