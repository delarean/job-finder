from __future__ import annotations

import unittest

from jobsearch_agent.db.query_builder import build_hybrid_query
from jobsearch_agent.models import SearchRequest


class QueryBuilderTests(unittest.TestCase):
    def test_build_hybrid_query_includes_filters(self) -> None:
        query = build_hybrid_query(
            SearchRequest(
                query="python langgraph",
                location="Madrid",
                remote="remote",
                company="OpenAI",
            )
        )
        self.assertEqual(query.lexical_query, "python & langgraph")
        self.assertEqual(query.semantic_query, "python langgraph")
        self.assertEqual(query.filters["location"], "Madrid")
        self.assertEqual(query.filters["remote_type"], "remote")
        self.assertEqual(query.filters["company"], "OpenAI")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
