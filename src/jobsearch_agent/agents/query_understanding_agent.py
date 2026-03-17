from __future__ import annotations

from jobsearch_agent.models import SearchRequest


def understand_query(request: SearchRequest) -> dict[str, object]:
    hints: list[str] = []
    if request.location is None:
        hints.append("location")
    if request.remote is None:
        hints.append("remote")
    return {
        "query": request.query.strip(),
        "clarifying_fields": hints,
        "suggested_filters": {
            "location": request.location,
            "remote_type": request.remote,
            "company": request.company,
            "recency_days": request.recency_days,
        },
    }
