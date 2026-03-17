from __future__ import annotations

from dataclasses import dataclass, field

from jobsearch_agent.models import JobRecord, SearchRequest


@dataclass
class SearchState:
    request: SearchRequest
    lexical_query: str = ""
    semantic_query: str = ""
    filters: dict[str, object] = field(default_factory=dict)
    candidate_ids: list[str] = field(default_factory=list)
    results: list[JobRecord] = field(default_factory=list)
    analysis: dict[str, object] = field(default_factory=dict)
