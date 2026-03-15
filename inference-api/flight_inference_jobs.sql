CREATE TABLE IF NOT EXISTS flight_inference_jobs (
    job_id VARCHAR(36) PRIMARY KEY,
    status VARCHAR(20) NOT NULL CHECK (status IN ('queued', 'running', 'succeeded', 'failed')),
    request_json JSONB NOT NULL,
    result_json JSONB,
    error_text TEXT,
    webhook_url TEXT,
    webhook_sent BOOLEAN NOT NULL DEFAULT FALSE,
    webhook_status_code INTEGER,
    webhook_error_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_flight_inference_jobs_status
    ON flight_inference_jobs (status);

CREATE INDEX IF NOT EXISTS idx_flight_inference_jobs_created_at
    ON flight_inference_jobs (created_at);
