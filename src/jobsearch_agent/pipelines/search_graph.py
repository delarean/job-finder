from __future__ import annotations

from jobsearch_agent.agents.analysis_agent import analyze_jobs
from jobsearch_agent.agents.export_agent import export_results
from jobsearch_agent.agents.hybrid_search_agent import run_hybrid_search
from jobsearch_agent.agents.query_builder_agent import build_query
from jobsearch_agent.agents.query_understanding_agent import understand_query
from jobsearch_agent.agents.retrieve_agent import retrieve_results
from jobsearch_agent.db.base import BaseStore
from jobsearch_agent.models import SearchRequest


def run_search_pipeline(
    store: BaseStore,
    request: SearchRequest,
    embedding: list[float],
) -> dict[str, object]:
    understanding = understand_query(request)
    query = build_query(request)
    ranked = run_hybrid_search(store, request, embedding)
    results = retrieve_results(store, ranked)
    analysis = analyze_jobs(results) if request.analysis else {}
    export_path = export_results(results)
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
