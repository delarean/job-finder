from __future__ import annotations

from collections import Counter

from jobsearch_agent.models import JobRecord


def analyze_jobs(results: list[JobRecord]) -> dict[str, object]:
    companies = Counter(job.company for job in results if job.company)
    locations = Counter(job.location for job in results if job.location)
    return {
        "count": len(results),
        "top_companies": companies.most_common(5),
        "top_locations": locations.most_common(5),
    }
