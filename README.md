# Job Search Agent

Agentic job-search system with:

- **Airflow** for scheduled ingestion
- **LangGraph** for interactive search orchestration
- **PostgreSQL + pgvector** for hybrid retrieval

## Architecture

### Ingestion

Airflow runs a DAG with these stages:

1. discover
2. fetch/extract
3. normalize/dedupe
4. embed
5. persist

### Search

The app runs a LangGraph-style search pipeline:

1. understand query
2. build query
3. hybrid search
4. retrieve
5. analyze
6. export

## Quick start

1. Copy `.env.example` to `.env`
2. Start local services with Docker Compose
3. Create the database schema
4. Trigger ingestion
5. Run search from the CLI

## Example commands

```bash
jobsearch-agent search --query "python langgraph remote"
jobsearch-agent analyze --query "ml engineer spain remote"
```

## Current status

This repository currently contains the initial implementation scaffold:

- project configuration
- PostgreSQL schema
- Airflow DAG skeleton
- ingestion modules
- search modules
- CLI
- unit tests for core query logic and DAG structure
