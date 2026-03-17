from __future__ import annotations

import unittest

from jobsearch_agent.db.query_builder import score_candidate


class HybridRankingTests(unittest.TestCase):
    def test_hybrid_ranking_prefers_balanced_relevance(self) -> None:
        exact = score_candidate(0.9, 0.3, recency_boost=0.6, exact_match_boost=1.0)
        semantic = score_candidate(0.3, 0.9, recency_boost=0.6, exact_match_boost=0.0)
        self.assertGreater(exact, semantic)

    def test_hybrid_ranking_can_surface_semantic_match(self) -> None:
        semantic = score_candidate(0.2, 0.95, recency_boost=0.6)
        weak = score_candidate(0.1, 0.3, recency_boost=0.1)
        self.assertGreater(semantic, weak)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
