from __future__ import annotations

from pathlib import Path
import unittest


class AirflowDagStructureTests(unittest.TestCase):
    def test_airflow_dag_contains_expected_tasks(self) -> None:
        content = Path("airflow/dags/job_ingestion_dag.py").read_text(encoding="utf-8")
        self.assertIn('task_id="discover"', content)
        self.assertIn('task_id="fetch_extract"', content)
        self.assertIn('task_id="normalize"', content)
        self.assertIn('task_id="embed"', content)
        self.assertIn('task_id="persist"', content)
        self.assertIn("discover >> fetch_extract >> normalize >> embed >> persist", content)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
