from __future__ import annotations


def fetch_and_extract(candidates: list[dict]) -> list[dict]:
    extracted: list[dict] = []
    for candidate in candidates:
        extracted.append(
            {
                "source": candidate.get("source", "unknown"),
                "title": candidate.get("title", ""),
                "company": candidate.get("company", ""),
                "canonical_url": candidate.get("url", ""),
                "description_text": candidate.get("description", ""),
                "location": candidate.get("location"),
                "remote_type": candidate.get("remote_type"),
                "date_posted": candidate.get("date_posted"),
            }
        )
    return extracted
