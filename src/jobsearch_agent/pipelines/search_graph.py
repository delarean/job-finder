from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from jobsearch_agent.agents.analysis_agent import analyze_jobs
from jobsearch_agent.agents.export_agent import export_results
from jobsearch_agent.agents.hybrid_search_agent import run_hybrid_search
from jobsearch_agent.agents.query_builder_agent import build_query
from jobsearch_agent.agents.query_understanding_agent import understand_query
from jobsearch_agent.agents.retrieve_agent import retrieve_results
from jobsearch_agent.db.base import BaseStore
from jobsearch_agent.models import SearchRequest, SearchRunSummary


def run_search_pipeline(
    store: BaseStore,
    request: SearchRequest,
    embedding: list[float],
) -> dict[str, object]:
    run = SearchRunSummary(
        run_id=str(uuid4()),
        query=request.query,
        started_at=datetime.now(timezone.utc),
    )
    store.record_search_run(run)
    understanding = understand_query(request)
    query = build_query(request)
    ranked = run_hybrid_search(store, request, embedding)
    results = retrieve_results(store, ranked)
    analysis = analyze_jobs(results) if request.analysis else {}
    export_path = export_results(results)
    run.clarified_query = understanding["query"]
    run.filters = understanding["suggested_filters"]
    run.match_count = len(results)
    run.export_path = export_path
    run.analysis = analysis
    run.completed_at = datetime.now(timezone.utc)
    store.record_search_run(run)
    return {
        "understanding": understanding,
        "query": query,
        "ranked": ranked,
        "results": results,
        "analysis": analysis,
        "export_path": export_path,
    }


def build_langgraph_search_app():  # pragma: no cover - optional dependency wiring
    from langgraph.graph import END, START, StateGraph

    graph = StateGraph(dict)

    graph.add_node("understand", lambda state: {"understanding": understand_query(state["request"])})
    graph.add_node("build_query", lambda state: {"query": build_query(state["request"])})
    graph.add_edge(START, "understand")
    graph.add_edge("understand", "build_query")
    graph.add_edge("build_query", END)
    return graph.compile()
