from __future__ import annotations

from jobsearch_agent.db.query_builder import HybridQuery, build_hybrid_query
from jobsearch_agent.models import SearchRequest


def build_query(request: SearchRequest) -> HybridQuery:
    return build_hybrid_query(request)
