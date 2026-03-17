from __future__ import annotations

from jobsearch_agent.models import IngestionRequest
from jobsearch_agent.sources.remoteok import discover_remoteok_jobs
from jobsearch_agent.sources.tavily_discovery import discover_with_tavily


def discover_candidates(request: IngestionRequest) -> list[dict]:
    candidates: list[dict] = []
    if not request.sources or "remoteok" in request.sources:
        candidates.extend(discover_remoteok_jobs())
    if not request.sources or "tavily" in request.sources:
        candidates.extend(discover_with_tavily())
    return candidates
