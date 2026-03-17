# Test Spec: Agentic Job Search App (Airflow Ingestion + LangGraph Search + PostgreSQL/pgvector)

Date: 2026-03-17  
Related PRD: `.omx/plans/prd-job-search-agentic-app-2026-03-17.md`

## Test Strategy

Test ingestion and search as separate systems:

- Airflow ingestion is validated as a scheduled batch workflow.
- LangGraph search is validated as an interactive retrieval workflow.
- PostgreSQL + pgvector is validated as the shared storage/retrieval layer.

Keep tests deterministic with fixtures and mocks. Avoid live-network dependency in CI.

## Unit Tests

### `tests/unit/test_models.py`

- Validate `IngestionRequest`, `SearchRequest`, and `JobRecord`.
- Validate required canonical fields, filters, and date handling.

### `tests/unit/test_dedup.py`

- Same job ingested twice -> one canonical record.
- Same job from two sources with same canonical URL -> one canonical record or expected merge behavior.

### `tests/unit/test_recency.py`

- Search-time recency filters include the boundary date.
- Stale jobs are excluded from search/export.

### `tests/unit/test_postgres_store.py`

- Schema initialization succeeds.
- Upsert by `dedupe_key` works.
- Ingestion-run metadata and search-run metadata are stored separately.
- FTS document and embedding fields are stored as expected.

### `tests/unit/test_query_builder.py`

- Query understanding output maps to lexical terms, vector text, and metadata filters.
- Generated SQL/search parameters reflect chosen filters correctly.

### `tests/unit/test_hybrid_ranking.py`

- Exact lexical match can outrank weak semantic matches when weighted to do so.
- Strong semantic matches can surface even when title wording differs.
- Recency boost and hard filters are applied correctly.

### `tests/unit/test_airflow_dag_structure.py`

- DAG parses correctly.
- Schedule exists and is configurable.
- Task dependency order is:
  - discover
  - fetch_extract
  - normalize
  - embed
  - persist

## Integration Tests

### `tests/integration/test_airflow_ingestion_flow.py`

- Airflow ingestion flow runs end to end on fixtures.
- Direct adapter records are normalized, embedded, and stored.
- Ingestion run metadata includes Airflow run identity.

### `tests/integration/test_search_pipeline.py`

- Search graph runs entirely from preloaded PostgreSQL data.
- Query understanding -> query building -> hybrid search -> retrieve -> export flow returns expected rows.

### `tests/integration/test_postgres_pgvector_search.py`

- Full-text search returns expected lexical matches.
- Vector similarity returns expected semantic neighbors.
- Hybrid ranking behaves consistently for mixed lexical/semantic cases.

### `tests/integration/test_tavily_discovery.py`

- Tavily responses map to candidate listing URLs or source candidates.
- Tavily failure is captured without crashing the whole ingestion run.

### `tests/integration/test_partial_failure.py`

- One ingestion source fails, another succeeds.
- Search still works against the successfully ingested subset.

## End-to-End Smoke Tests

### Ingestion smoke test

1. Start local PostgreSQL with pgvector enabled.
2. Start local Airflow services.
3. Trigger the ingestion DAG.
4. Confirm job records are inserted.
5. Confirm embeddings and FTS fields are present.
6. Confirm ingestion summary metrics are printed/stored.

### Search smoke test

1. Run `search --query ...` against the populated PostgreSQL database.
2. Confirm the command returns matches without a web call.
3. Confirm lexical + semantic + metadata filters all affect the result set.
4. Confirm `output/jobs.csv` is written.

### Analysis smoke test

1. Run `search --analysis` or `analyze`.
2. Confirm the app returns a small summary over the retrieved result set.
3. Confirm analysis operates on stored/retrieved data, not fresh web fetches.

## Fixtures Needed

- One recent valid job with exact keyword match
- One semantically similar job with different wording
- One stale job
- Two duplicates across runs
- Two duplicates across different sources
- One malformed source payload
- One Tavily discovery payload
- One Tavily failure payload

## Exit Criteria

- All unit tests pass.
- Airflow DAG structure tests pass.
- All ingestion integration tests pass.
- All search integration tests pass.
- PostgreSQL + pgvector hybrid retrieval works locally.
- Search works from local storage without network access.
- CSV export contains only retrieved matching jobs.
- Re-ingestion does not create duplicate records.
- Optional analysis runs on retrieved results successfully.
