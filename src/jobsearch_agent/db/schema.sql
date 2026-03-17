CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS job_records (
    job_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    canonical_url TEXT NOT NULL,
    description_text TEXT NOT NULL,
    date_posted TIMESTAMPTZ NULL,
    location TEXT NULL,
    remote_type TEXT NULL,
    employment_type TEXT NULL,
    salary_text TEXT NULL,
    tags TEXT[] NOT NULL DEFAULT '{}',
    dedupe_key TEXT NOT NULL UNIQUE,
    embedding vector(1536),
    fts_document tsvector
);

CREATE INDEX IF NOT EXISTS idx_job_records_company ON job_records (company);
CREATE INDEX IF NOT EXISTS idx_job_records_location ON job_records (location);
CREATE INDEX IF NOT EXISTS idx_job_records_remote_type ON job_records (remote_type);
CREATE INDEX IF NOT EXISTS idx_job_records_date_posted ON job_records (date_posted DESC);
CREATE INDEX IF NOT EXISTS idx_job_records_fts ON job_records USING GIN (fts_document);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    run_id TEXT PRIMARY KEY,
    airflow_run_id TEXT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ NULL,
    candidate_count INTEGER NOT NULL DEFAULT 0,
    fetched_count INTEGER NOT NULL DEFAULT 0,
    normalized_count INTEGER NOT NULL DEFAULT 0,
    embedded_count INTEGER NOT NULL DEFAULT 0,
    upserted_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'running'
);

CREATE TABLE IF NOT EXISTS search_runs (
    run_id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    clarified_query TEXT NULL,
    filters_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ NULL,
    match_count INTEGER NOT NULL DEFAULT 0,
    export_path TEXT NULL,
    analysis_json JSONB NOT NULL DEFAULT '{}'::jsonb
);
