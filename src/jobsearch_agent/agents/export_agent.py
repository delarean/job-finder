from __future__ import annotations

from pathlib import Path

from jobsearch_agent.export.csv_writer import write_jobs_csv
from jobsearch_agent.models import JobRecord


def export_results(results: list[JobRecord], output_path: str = "output/jobs.csv") -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_jobs_csv(results, path)
    return str(path)
