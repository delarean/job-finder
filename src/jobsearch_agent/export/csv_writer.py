from __future__ import annotations

import csv
from pathlib import Path

from jobsearch_agent.models import JobRecord


def write_jobs_csv(records: list[JobRecord], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "job_id",
                "source",
                "title",
                "company",
                "location",
                "remote_type",
                "canonical_url",
                "date_posted",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "job_id": record.job_id,
                    "source": record.source,
                    "title": record.title,
                    "company": record.company,
                    "location": record.location,
                    "remote_type": record.remote_type,
                    "canonical_url": record.canonical_url,
                    "date_posted": record.date_posted.isoformat() if record.date_posted else "",
                }
            )
