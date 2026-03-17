# PRD: Agentic Job Search App (Airflow Ingestion + LangGraph Search + PostgreSQL/pgvector)

Date: 2026-03-17  
Status: Revised via `$plan`  
Chosen architecture:
- **Airflow for ingestion orchestration**
- **LangGraph app for interactive search**
- **PostgreSQL + full-text search + pgvector for storage/retrieval**

Repo context: greenfield; repository currently contains `.git/` and `.omx/` only, so this plan assumes a fresh implementation.

## Revision Summary

This revision locks the system into two separate operational surfaces:

1. **Ingestion platform** — Airflow schedules and monitors batch ingestion DAGs.
2. **Search application** — a Python/LangGraph app serves interactive search, filtering, analysis, and export.

This matches the intended operating model:

- ingestion is scheduled and batch-oriented,
- search is interactive and query-driven,
- PostgreSQL is the system of record,
- pgvector enables semantic retrieval,
- analysis runs on stored data rather than fresh fetches.

## Why This Split Was Chosen

Airflow is a strong fit for scheduled, batch-oriented workflows with retries, scheduling, monitoring, and dependency management. Search is not a batch workflow, so it should stay outside Airflow in the application layer.

That means:

- **Airflow** handles:
  - scheduled discovery
  - fetching
  - normalization
  - embedding
  - persistence/upserts
- **LangGraph app** handles:
  - user query understanding
  - hybrid retrieval
  - follow-up question handling
  - filtering
  - analysis
  - CSV export

## Assumptions

- Build a CLI-first app before adding any web UI.
- Use Python as the runtime.
- Use Airflow only for ingestion orchestration.
- Use LangGraph only for the interactive search side.
- Use LangChain where it adds value for query understanding, extraction prompts, embeddings, and reranking.
- Use PostgreSQL as the canonical database for records, runs, and analysis queries.
- Use `pgvector` for semantic similarity search over job descriptions/titles.
- Use PostgreSQL full-text search for lexical matching and keyword constraints.
- Support metadata filters such as location, remote, recency, company, and employment type.
- Define “recently posted” as jobs posted within the last 7 days by default, configurable via CLI/config.
- Use direct structured source adapters first, with Tavily as discovery fallback.

## Requirements Summary

Build an agentic job-search system that:

1. Runs scheduled ingestion jobs in Airflow.
2. Stores canonical job records plus embeddings in PostgreSQL.
3. Supports a separate interactive search app that uses the stored corpus first.
4. Supports hybrid retrieval:
   - lexical search,
   - semantic/vector search,
   - structured metadata filters.
5. Supports follow-up clarification questions or inferred filters from the user request.
6. Can optionally analyze retrieved result sets.
7. Exports recent matching jobs to CSV.
8. Keeps ingestion and search independently deployable and testable.

## Goals

- Decouple ingestion from search.
- Use Airflow for reliable recurring ingestion.
- Support semantic search from v1.
- Preserve strong structured filtering.
- Keep canonical data in one durable database.
- Enable later analytics directly with SQL over ingested jobs.
- Keep the architecture extensible for API/web deployment later.

## Non-Goals (v1)

- Browser automation over arbitrary job boards.
- Hosted multi-tenant SaaS deployment.
- Automated job applications.
- Real-time streaming ingestion.
- Full personalized career coaching.

## Selected Architecture

## Pipeline A — Airflow Ingestion Platform

Purpose: build and maintain the searchable job corpus on a schedule.

### Airflow responsibilities

- schedule runs
- orchestrate task dependencies
- retry failed tasks
- capture run status and logs
- support manual backfills/reruns later if needed

### Ingestion DAG stages

1. **Discovery task**
   - Finds candidate job listings, feeds, or company career pages.
   - Uses direct adapters first.
   - Uses Tavily as fallback discovery.

2. **Fetch / Extract task**
   - Retrieves source payloads or page content.
   - Extracts:
     - title
     - company
     - location
     - description
     - canonical URL
     - posting date
     - other metadata

3. **Normalize / Deduplicate task**
   - Maps external data into canonical `JobRecord`.
   - Computes stable `dedupe_key`.
   - Canonicalizes company names, URLs, locations, remote flags, and dates.

4. **Embedding task**
   - Builds embeddings for searchable text such as title + summary + description.

5. **Persist / Index task**
   - Upserts canonical records into PostgreSQL.
   - Updates:
     - relational tables
     - full-text search fields
     - pgvector embedding column
     - ingestion run metadata

### Initial scheduling model

- one Airflow DAG for the main ingestion pipeline
- schedule: configurable, e.g. every 6 hours
- support manual trigger for testing/backfill

### Airflow boundary

Airflow does **not** handle:

- end-user search requests
- conversational follow-up questions
- interactive retrieval/export flows

Those stay in the app.

## Pipeline B — LangGraph Search Application

Purpose: answer user job searches from the local indexed corpus.

### Search app stages

1. **Query Understanding Agent**
   - Interprets the user request.
   - Expands synonyms.
   - Identifies missing constraints.
   - Can ask or suggest follow-up questions such as:
     - remote vs onsite,
     - preferred regions,
     - salary constraints,
     - seniority,
     - recency window.

2. **Query Builder Agent**
   - Produces:
     - lexical query,
     - embedding query text,
     - metadata filters,
     - ranking weights.

3. **Hybrid Search Agent**
   - Uses PostgreSQL full-text search for lexical recall.
   - Uses pgvector for semantic similarity.
   - Applies structured SQL filters.
   - Combines scores into ranked candidate ids.

4. **Retrieve Agent**
   - Loads full records for ranked ids.

5. **Analysis Agent** (optional but planned)
   - Produces summaries such as:
     - top companies,
     - common skills,
     - role clusters,
     - location distributions,
     - recency breakdown.

6. **Export Agent**
   - Writes matching jobs to CSV.
   - Produces a concise run summary.

### Canonical runtime flow

`Airflow ingestion DAG: discover -> fetch/extract -> normalize/dedupe -> embed -> persist/index`

`LangGraph search app: user request -> understand -> build hybrid query -> lexical + vector + filters -> retrieve -> analyze? -> export CSV`

## Why PostgreSQL + pgvector Was Chosen

### Benefits

- One durable system for:
  - canonical job records,
  - ingestion history,
  - search history,
  - embeddings,
  - analytics.
- Strong relational model for deduplication and upserts.
- Built-in full-text search for exact/keyword-heavy matching.
- Vector similarity support for semantic retrieval.
- Easy support for filters like date/location/remote/company.
- Better long-term architecture than SQLite for this product direction.

### Tradeoffs

- More setup than SQLite.
- Requires a local or containerized PostgreSQL instance.
- Adds operational complexity for development/testing.

## Retrieval Strategy

### Recommended ingestion sources

1. **Direct structured adapters first**
   - RemoteOK
   - RSS feeds
   - Greenhouse-hosted boards
   - Lever-hosted boards
   - any stable source payloads

2. **Tavily as discovery fallback**
   - discover fresh listings and long-tail company job pages
   - find likely sources when no direct adapter exists
   - optionally extract content for unstructured pages

### Search modes

#### Mode 1 — Lexical first
Best for:
- exact titles
- specific technologies
- company names

#### Mode 2 — Semantic first
Best for:
- fuzzy role phrasing
- adjacent titles
- wording variation

#### Mode 3 — Hybrid ranked retrieval
Recommended default.

Combines:
- text relevance
- vector similarity
- recency boost
- filter compliance
- exact title/company boosts

## Canonical Data Model

### `job_records`

- `job_id`
- `source`
- `source_type`
- `source_job_id`
- `source_url`
- `canonical_url`
- `title`
- `company`
- `location`
- `remote_type`
- `employment_type`
- `salary_text`
- `description_text`
- `description_snippet`
- `search_text`
- `date_posted`
- `date_seen`
- `date_ingested`
- `tags`
- `dedupe_key`
- `embedding`
- `fts_document`
- `raw_payload_ref`

### `ingestion_runs`

- `run_id`
- `airflow_run_id`
- `started_at`
- `completed_at`
- `source_count`
- `candidate_count`
- `fetched_count`
- `normalized_count`
- `deduped_count`
- `embedded_count`
- `upserted_count`
- `error_count`
- `status`

### `search_runs`

- `run_id`
- `query`
- `clarified_query`
- `filters_json`
- `started_at`
- `completed_at`
- `match_count`
- `export_path`
- `analysis_json`

## Proposed PostgreSQL Schema Concerns

- `job_records` table with unique constraints on `dedupe_key` and/or normalized canonical URL strategy
- full-text search document column
- vector column for embeddings
- indexes for:
  - recency/date
  - company
  - remote_type
  - location
  - source
- run tables for ingestion and search auditability

## Proposed File Layout

```text
pyproject.toml
.env.example
README.md
docker-compose.yml
airflow/
airflow/dags/job_ingestion_dag.py
airflow/plugins/
airflow/include/
src/jobsearch_agent/__init__.py
src/jobsearch_agent/config.py
src/jobsearch_agent/models.py
src/jobsearch_agent/state.py
src/jobsearch_agent/cli.py
src/jobsearch_agent/db/base.py
src/jobsearch_agent/db/postgres_store.py
src/jobsearch_agent/db/query_builder.py
src/jobsearch_agent/db/schema.sql
src/jobsearch_agent/db/migrations/
src/jobsearch_agent/pipelines/search_graph.py
src/jobsearch_agent/agents/query_understanding_agent.py
src/jobsearch_agent/agents/query_builder_agent.py
src/jobsearch_agent/agents/hybrid_search_agent.py
src/jobsearch_agent/agents/retrieve_agent.py
src/jobsearch_agent/agents/analysis_agent.py
src/jobsearch_agent/agents/export_agent.py
src/jobsearch_agent/ingestion/discovery.py
src/jobsearch_agent/ingestion/fetch_extract.py
src/jobsearch_agent/ingestion/normalize.py
src/jobsearch_agent/ingestion/embed.py
src/jobsearch_agent/ingestion/persist.py
src/jobsearch_agent/sources/base.py
src/jobsearch_agent/sources/remoteok.py
src/jobsearch_agent/sources/tavily_discovery.py
src/jobsearch_agent/export/csv_writer.py
tests/unit/test_models.py
tests/unit/test_dedup.py
tests/unit/test_recency.py
tests/unit/test_postgres_store.py
tests/unit/test_query_builder.py
tests/unit/test_hybrid_ranking.py
tests/unit/test_airflow_dag_structure.py
tests/integration/test_airflow_ingestion_flow.py
tests/integration/test_search_pipeline.py
tests/integration/test_tavily_discovery.py
tests/integration/test_postgres_pgvector_search.py
tests/fixtures/
output/jobs.csv
```

## Acceptance Criteria

1. The Airflow ingestion pipeline can run independently from the LangGraph search app.
2. The search app can return results from PostgreSQL without making a web request.
3. Running the ingestion DAG stores canonicalized job records in PostgreSQL.
4. Running the ingestion DAG also stores embeddings for searchable job records.
5. Running search performs hybrid retrieval using:
   - PostgreSQL full-text search,
   - pgvector similarity,
   - structured metadata filters.
6. The system supports filters for:
   - recency,
   - location,
   - remote type,
   - company.
7. Duplicate jobs across repeated ingestion runs are not stored twice.
8. A failed source or Tavily request does not crash the entire ingestion DAG run.
9. Search results can be exported to `output/jobs.csv`.
10. The app can optionally produce an analysis summary over the retrieved result set.
11. Ingestion-run metrics and search-run metrics are stored separately.
12. At least one structured source adapter and one Tavily-backed discovery path are covered by tests.
13. Airflow scheduling/retry orchestration exists only on ingestion, not on interactive search.

## Implementation Steps

### Phase 1 — Bootstrap

1. Create `pyproject.toml` with:
   - Python package metadata
   - LangGraph
   - LangChain
   - Pydantic
   - PostgreSQL client library
   - pgvector client support
   - Airflow dependency strategy
   - test tooling
2. Add `.env.example` for:
   - Postgres connection string
   - Tavily API key
   - embedding model settings
   - Airflow environment values
3. Add `docker-compose.yml` for local PostgreSQL + Airflow development.
4. Add `README.md` describing the Airflow/LangGraph split.

### Phase 2 — Domain and configuration

5. Create `src/jobsearch_agent/models.py`
   - `IngestionRequest`
   - `SearchRequest`
   - `JobRecord`
   - `IngestionRunSummary`
   - `SearchRunSummary`
6. Create `src/jobsearch_agent/config.py`
   - Postgres DSN
   - source toggles
   - recency defaults
   - ranking weights
   - Airflow schedule settings
7. Create `src/jobsearch_agent/state.py`
   - LangGraph state models for search.

### Phase 3 — Database layer

8. Implement `src/jobsearch_agent/db/base.py`
   - abstract persistence/search interface.
9. Implement `src/jobsearch_agent/db/schema.sql`
   - relational tables
   - FTS columns/indexes
   - pgvector column/indexes
10. Implement `src/jobsearch_agent/db/postgres_store.py`
    - connection management
    - upsert logic
    - ingestion/search run persistence
11. Implement `src/jobsearch_agent/db/query_builder.py`
    - lexical query generation
    - filter SQL construction
    - hybrid ranking query assembly

### Phase 4 — Ingestion task modules

12. Create `src/jobsearch_agent/ingestion/discovery.py`
    - direct adapters first
    - Tavily fallback discovery
13. Create `src/jobsearch_agent/ingestion/fetch_extract.py`
    - fetch payloads/pages
    - extract structured fields
14. Create `src/jobsearch_agent/ingestion/normalize.py`
    - canonicalization
    - date parsing
    - dedupe-key generation
15. Create `src/jobsearch_agent/ingestion/embed.py`
    - embedding generation for searchable text
16. Create `src/jobsearch_agent/ingestion/persist.py`
    - upsert records
    - update FTS/vector fields

### Phase 5 — Airflow ingestion orchestration

17. Create `airflow/dags/job_ingestion_dag.py`
    - DAG schedule
    - task dependencies
    - retry policy
    - manual trigger support
18. Wire Airflow tasks to the ingestion modules:
    - `discover`
    - `fetch_extract`
    - `normalize`
    - `embed`
    - `persist`
19. Add ingestion run metadata propagation from Airflow run ids into PostgreSQL.

### Phase 6 — Search app

20. Create `src/jobsearch_agent/agents/query_understanding_agent.py`
    - infer filters and missing constraints
21. Create `src/jobsearch_agent/agents/query_builder_agent.py`
    - build lexical + vector + metadata query package
22. Create `src/jobsearch_agent/agents/hybrid_search_agent.py`
    - execute hybrid retrieval in PostgreSQL
23. Create `src/jobsearch_agent/agents/retrieve_agent.py`
    - load full records by ranked ids
24. Create `src/jobsearch_agent/agents/analysis_agent.py`
    - summarize skills/companies/locations/recency patterns
25. Create `src/jobsearch_agent/agents/export_agent.py`
    - CSV export and final summary
26. Create `src/jobsearch_agent/pipelines/search_graph.py`
    - `understand -> build_query -> hybrid_search -> retrieve -> analyze? -> export`

### Phase 7 — Sources

27. Create `src/jobsearch_agent/sources/base.py`
    - common source interface
28. Implement `src/jobsearch_agent/sources/remoteok.py`
29. Implement `src/jobsearch_agent/sources/tavily_discovery.py`
    - domain/date scoping
    - candidate extraction
    - mapping to ingestion candidates

### Phase 8 — CLI and UX

30. Create `src/jobsearch_agent/cli.py` commands such as:
    - `search`
    - `export`
    - `analyze`
    - `trigger-ingest` (optional helper that calls Airflow trigger API/CLI later)
31. Add CLI/config flags such as:
    - `--query`
    - `--location`
    - `--remote`
    - `--days`
    - `--company`
    - `--top-k`
    - `--analysis`

### Phase 9 — Tests

32. Add unit tests for schema, dedupe, recency, query building, hybrid ranking, and DAG structure.
33. Add integration tests for Airflow ingestion flow and the search app separately.
34. Add integration tests covering PostgreSQL + pgvector hybrid retrieval behavior.
35. Add fixture-based Tavily discovery tests and source adapter tests.

## Risks and Mitigations

### Risk: Airflow adds operational overhead
- **Mitigation:** use Airflow only for ingestion, not for interactive search.

### Risk: semantic results are broad but imprecise
- **Mitigation:** combine vector similarity with lexical scoring and hard filters.

### Risk: Tavily-only ingestion is noisy
- **Mitigation:** use Tavily as fallback discovery, not the only connector.

### Risk: embeddings increase ingestion cost/latency
- **Mitigation:** embed only normalized searchable text and support incremental embedding.

### Risk: stored records become stale
- **Mitigation:** schedule recurring ingestion and keep `date_ingested`.

### Risk: duplicate jobs across sources
- **Mitigation:** canonical URLs + normalized dedupe key + source-aware merge rules.

## Verification Steps

1. Validate the Airflow DAG loads correctly.
2. Trigger the ingestion DAG manually and confirm records persist in PostgreSQL.
3. Verify embeddings are written for eligible records.
4. Verify failed ingestion tasks retry according to policy.
5. Run search against PostgreSQL with networking disabled and confirm results still return.
6. Verify hybrid retrieval returns expected records for:
   - exact keyword queries,
   - fuzzy semantic queries,
   - filtered queries.
7. Verify duplicate ingestion does not create duplicate stored records.
8. Verify recency/date filters work at search time.
9. Verify CSV export only includes retrieved matching records.
10. Verify optional analysis output is generated from retrieved results.
11. Simulate Tavily failure and confirm direct adapters still ingest successfully.
12. Simulate source failure and confirm ingestion run summaries capture partial success.

## Final Architecture Decision

- **Ingestion orchestration:** Airflow
- **Search orchestration:** LangGraph
- **Canonical database:** PostgreSQL
- **Semantic retrieval:** pgvector
- **Keyword retrieval:** PostgreSQL full-text search
- **Filtering:** SQL metadata filters
- **Source strategy:** direct adapters first, Tavily fallback
- **Default search mode:** hybrid retrieval
- **Analysis path:** SQL + agent summary over retrieved result set

## References Used for This Revision

- Airflow overview: https://airflow.apache.org/docs/apache-airflow/stable/index.html
- Airflow scheduler: https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/scheduler.html
- Airflow DAG concepts: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html
- PostgreSQL full-text search docs: https://www.postgresql.org/docs/current/textsearch.html
- pgvector official repository: https://github.com/pgvector/pgvector
- Tavily docs: https://docs.tavily.com/documentation/api-reference/endpoint/search
