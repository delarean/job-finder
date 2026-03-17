from __future__ import annotations

from jobsearch_agent.db.base import BaseStore
from jobsearch_agent.models import SearchRequest


def run_hybrid_search(
    store: BaseStore,
    request: SearchRequest,
    embedding: list[float],
) -> list[dict]:
    return store.hybrid_search(request, embedding)
