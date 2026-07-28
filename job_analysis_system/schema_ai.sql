-- New tables for AI-powered job analysis and recommendation.
-- Run this once against your existing jobs.db (or whatever you call it).
--
-- IMPORTANT: this assumes your existing jobs table has an integer primary
-- key called "id". If yours is named differently (e.g. job_id), change the
-- FOREIGN KEY lines below to match before running this.

CREATE TABLE IF NOT EXISTS job_analysis (
    job_id INTEGER PRIMARY KEY,
    skills TEXT,                   -- JSON array, e.g. ["Python", "AWS", "Docker"]
    seniority_level TEXT,          -- intern / junior / mid / senior / lead
    min_experience_years REAL,
    salary_min REAL,
    salary_max REAL,
    job_type TEXT,                 -- fulltime / contract / remote / hybrid / onsite
    summary TEXT,                  -- one-sentence AI-generated summary
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

CREATE TABLE IF NOT EXISTS job_embeddings (
    job_id INTEGER PRIMARY KEY,
    embedding BLOB NOT NULL,       -- serialized float32 numpy array
    model_name TEXT NOT NULL,      -- e.g. 'all-MiniLM-L6-v2'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

CREATE TABLE IF NOT EXISTS market_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_start DATE,
    period_end DATE,
    narrative TEXT,                -- AI-generated paragraph for the dashboard
    stats_json TEXT,                -- the raw numbers the narrative was built from
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
