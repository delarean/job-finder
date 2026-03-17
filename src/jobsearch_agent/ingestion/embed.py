from __future__ import annotations

from jobsearch_agent.models import JobRecord


def embed_records(records: list[JobRecord]) -> list[JobRecord]:
    for record in records:
        text = record.searchable_text()
        record.embedding = _fake_embedding(text)
    return records


def _fake_embedding(text: str, dimensions: int = 8) -> list[float]:
    bucket = [0.0] * dimensions
    for index, char in enumerate(text[:128]):
        bucket[index % dimensions] += (ord(char) % 31) / 31.0
    return bucket
