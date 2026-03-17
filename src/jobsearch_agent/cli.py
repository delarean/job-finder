from __future__ import annotations

import argparse
import json
from typing import Sequence

from jobsearch_agent.config import get_settings
from jobsearch_agent.db.postgres_store import PostgresStore
from jobsearch_agent.models import SearchRequest
from jobsearch_agent.pipelines.search_graph import run_search_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jobsearch-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search")
    _add_search_flags(search)

    analyze = subparsers.add_parser("analyze")
    _add_search_flags(analyze)
    analyze.set_defaults(analysis=True)

    export = subparsers.add_parser("export")
    _add_search_flags(export)

    return parser


def _add_search_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--query", required=True)
    parser.add_argument("--location")
    parser.add_argument("--remote")
    parser.add_argument("--company")
    parser.add_argument("--days", type=int)
    parser.add_argument("--top-k", type=int)
    parser.add_argument("--analysis", action="store_true")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = get_settings()
    request = SearchRequest(
        query=args.query,
        location=args.location,
        remote=args.remote,
        company=args.company,
        recency_days=args.days or settings.recency_days,
        top_k=args.top_k or settings.top_k,
        analysis=getattr(args, "analysis", False) or args.command == "analyze",
    )
    store = PostgresStore(settings.postgres_dsn)
    result = run_search_pipeline(store, request, embedding=[0.0] * 8)
    print(
        json.dumps(
            {
                "matches": len(result["results"]),
                "export_path": result["export_path"],
                "analysis": result["analysis"],
            },
            indent=2,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
