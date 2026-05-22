-- qualifying raw one row per driver per qualifuing session

CREATE TABLE IF NOT EXISTES qualifying_raw (
    id BIGSERIAL PRIMARY KEY,
    race_key TEXT NOT NULL,
    driver_code TEXT NOT NULL,
    driver_id TEXT NOT NULL,
    driver_name TEXT NOT NULL,
    team TEXT NOT NULL,
    team_id TEXT NOT NULL,
    position SMALLINT NOT NULL,
    q1_time TEXT q2_time TEXT q3_time TEXT best_lap_seconds FLOAT year SMALLINT NOT NULL round SMALLINT NOT NULL race_name TEXT NOT NULL circuit_id TEXT NOT NULL source TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT qualifying_raw_race_driver_unique UNIQUE (race_key, driver_code)
);

CREATE INDEX IF NOT EXISTS idx_qualifying_raw_race_key ON qualifying_raw (race_key);

CREATE INDEX IF NOT EXISTS idx_qualifying_raw_driver_year ON qualifying_raw (driver_code, year);

COMMENT ON TABLE qulifying_raw IS 
'RAW qualifying session data. Never modified after ingestion'
'Source of truth for feature engineering qualifying features.;