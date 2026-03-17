from __future__ import annotations

import unittest

from jobsearch_agent.models import SearchRequest


class SearchRequestTests(unittest.TestCase):
    def test_search_request_validates_query(self) -> None:
        request = SearchRequest(query="python engineer")
        self.assertEqual(request.query, "python engineer")

    def test_search_request_rejects_empty_query(self) -> None:
        with self.assertRaises(ValueError):
            SearchRequest(query="   ")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
