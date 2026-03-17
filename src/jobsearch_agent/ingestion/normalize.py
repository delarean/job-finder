from __future__ import annotations

import hashlib
from datetime import datetime
from urllib.parse import urlparse, urlunparse

from jobsearch_agent.models import JobRecord


def _canonicalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url.strip())
    normalized_path = parsed.path.rstrip("/") or parsed.path
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), normalized_path, "", "", ""))


def normalize_records(records: list[dict]) -> list[JobRecord]:
    normalized: list[JobRecord] = []
    for record in records:
        canonical_url = _canonicalize_url(record.get("canonical_url", "").strip())
        key_source = "|".join(
            [
                canonical_url or record.get("source", ""),
                record.get("company", "").strip().casefold(),
                record.get("title", "").strip().casefold(),
            ]
        )
        dedupe_key = hashlib.sha256(key_source.encode("utf-8")).hexdigest()
        date_posted = record.get("date_posted")
        if isinstance(date_posted, str):
            try:
                date_posted = datetime.fromisoformat(date_posted.replace("Z", "+00:00"))
            except ValueError:
                date_posted = None
        normalized.append(
            JobRecord(
                job_id=dedupe_key[:16],
                source=record.get("source", "unknown"),
                title=record.get("title", "").strip(),
                company=record.get("company", "").strip(),
                canonical_url=canonical_url,
                description_text=record.get("description_text", "").strip(),
                date_posted=date_posted,
                location=record.get("location"),
                remote_type=record.get("remote_type"),
                dedupe_key=dedupe_key,
            )
        )
    return normalized
