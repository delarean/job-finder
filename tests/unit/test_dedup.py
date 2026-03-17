from __future__ import annotations

import unittest

from jobsearch_agent.ingestion.normalize import normalize_records


class DedupTests(unittest.TestCase):
    def test_normalize_records_uses_canonical_url_for_cross_source_dedupe(self) -> None:
        records = normalize_records(
            [
                {
                    "source": "remoteok",
                    "title": "Python Engineer",
                    "company": "Example Co",
                    "canonical_url": "HTTPS://example.com/jobs/123?ref=remoteok",
                    "description_text": "Build AI tools",
                },
                {
                    "source": "tavily",
                    "title": " Python Engineer ",
                    "company": "example co",
                    "canonical_url": "https://example.com/jobs/123/",
                    "description_text": "Build AI tools",
                },
            ]
        )

        self.assertEqual(records[0].canonical_url, "https://example.com/jobs/123")
        self.assertEqual(records[0].dedupe_key, records[1].dedupe_key)
        self.assertEqual(records[0].job_id, records[1].job_id)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
