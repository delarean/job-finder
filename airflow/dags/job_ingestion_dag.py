from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from uuid import uuid4

from airflow import DAG
from airflow.operators.python import PythonOperator

from jobsearch_agent.config import get_settings
from jobsearch_agent.db.postgres_store import PostgresStore
from jobsearch_agent.ingestion.discovery import discover_candidates
from jobsearch_agent.ingestion.embed import embed_records
from jobsearch_agent.ingestion.fetch_extract import fetch_and_extract
from jobsearch_agent.ingestion.normalize import normalize_records
from jobsearch_agent.ingestion.persist import persist_records
from jobsearch_agent.models import IngestionRequest


def _discover(**context):
    request = IngestionRequest(sources=["remoteok", "tavily"])
    return discover_candidates(request)


def _fetch_extract(ti, **context):
    return fetch_and_extract(ti.xcom_pull(task_ids="discover"))


def _normalize(ti, **context):
    pulled = ti.xcom_pull(task_ids="fetch_extract")
    return [asdict(record) for record in normalize_records(pulled)]


def _embed(ti, **context):
    from jobsearch_agent.models import JobRecord

    records = [JobRecord(**payload) for payload in ti.xcom_pull(task_ids="normalize")]
    return [asdict(record) for record in embed_records(records)]


def _persist(ti, dag_run=None, **context):
    from jobsearch_agent.models import JobRecord

    settings = get_settings()
    store = PostgresStore(settings.postgres_dsn)
    records = [JobRecord(**payload) for payload in ti.xcom_pull(task_ids="embed")]
    run_id = getattr(dag_run, "run_id", str(uuid4()))
    return persist_records(store, records, airflow_run_id=run_id).run_id


with DAG(
    dag_id="job_ingestion",
    start_date=datetime(2026, 3, 17),
    schedule=get_settings().airflow_schedule,
    catchup=False,
    default_args={"retries": 2},
    tags=["jobsearch", "ingestion"],
) as dag:
    discover = PythonOperator(task_id="discover", python_callable=_discover)
    fetch_extract = PythonOperator(
        task_id="fetch_extract",
        python_callable=_fetch_extract,
    )
    normalize = PythonOperator(task_id="normalize", python_callable=_normalize)
    embed = PythonOperator(task_id="embed", python_callable=_embed)
    persist = PythonOperator(task_id="persist", python_callable=_persist)

    discover >> fetch_extract >> normalize >> embed >> persist
