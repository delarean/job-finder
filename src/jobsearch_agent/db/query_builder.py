from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from jobsearch_agent.models import SearchRequest


@dataclass
class HybridQuery:
    lexical_query: str
    semantic_query: str
    filters: dict[str, object] = field(default_factory=dict)
    top_k: int = 25


def build_hybrid_query(request: SearchRequest) -> HybridQuery:
    filters: dict[str, object] = {
        "posted_after": (
            datetime.now(timezone.utc) - timedelta(days=request.recency_days)
        ).isoformat(),
    }
    if request.location:
        filters["location"] = request.location
    if request.remote:
        filters["remote_type"] = request.remote
    if request.company:
        filters["company"] = request.company

    lexical = " & ".join(token for token in request.query.split() if token.strip())
    semantic = request.query.strip()
    return HybridQuery(
        lexical_query=lexical,
        semantic_query=semantic,
        filters=filters,
        top_k=request.top_k,
    )


def score_candidate(
    lexical_score: float,
    semantic_score: float,
    recency_boost: float = 0.0,
    exact_match_boost: float = 0.0,
    lexical_weight: float = 0.45,
    semantic_weight: float = 0.45,
    recency_weight: float = 0.05,
    exact_weight: float = 0.05,
) -> float:
    return (
        lexical_score * lexical_weight
        + semantic_score * semantic_weight
        + recency_boost * recency_weight
        + exact_match_boost * exact_weight
    )


def build_hybrid_sql(query: HybridQuery) -> str:
    return """
WITH ranked AS (
    SELECT
        job_id,
        title,
        company,
        ts_rank(fts_document, websearch_to_tsquery('english', %(lexical_query)s)) AS lexical_score,
        1 - (embedding <=> %(embedding)s) AS semantic_score,
        date_posted
    FROM job_records
    WHERE (%(location)s IS NULL OR location = %(location)s)
      AND (%(remote_type)s IS NULL OR remote_type = %(remote_type)s)
      AND (%(company)s IS NULL OR company = %(company)s)
      AND (date_posted IS NULL OR date_posted >= %(posted_after)s::timestamptz)
)
SELECT *
FROM ranked
ORDER BY lexical_score DESC, semantic_score DESC, date_posted DESC NULLS LAST
LIMIT %(top_k)s
""".strip()
