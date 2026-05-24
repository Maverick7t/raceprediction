"""
Unit tests — Pandera validation schemas.
 
WHEN TO RUN:
  Locally: after writing any schema in app/validation/schemas.py
    pytest tests/unit/test_validation.py -v
  CI: runs automatically on every push to main
"""
 
import pandas as pd
import pandera as pa
import pytest
 
from app.validation.schemas import QualifyingRawSchema, ResultsRawSchema, TelemetryRawSchema
 
 
class TestQualifyingSchema:
 
    def test_valid_rows_pass(self, qualifying_df):
        result = QualifyingRawSchema.validate(qualifying_df, lazy=True)
        assert len(result) == 2
 
    def test_position_out_of_range_fails(self, qualifying_df):
        df = qualifying_df.copy()
        df.loc[0, "position"] = 25
        with pytest.raises(pa.errors.SchemaErrors) as exc:
            QualifyingRawSchema.validate(df, lazy=True)
        assert "position" in exc.value.failure_cases["column"].values
 
    def test_q2_q3_nullable(self, qualifying_df):
        df = qualifying_df.copy()
        df.loc[0, "q2_time"] = None
        df.loc[0, "q3_time"] = None
        result = QualifyingRawSchema.validate(df, lazy=True)
        assert len(result) == 2
 
    def test_best_lap_seconds_nullable(self, qualifying_df):
        df = qualifying_df.copy()
        df["best_lap_seconds"] = None
        result = QualifyingRawSchema.validate(df, lazy=True)
        assert len(result) == 2
 
    def test_best_lap_too_fast_fails(self, qualifying_df):
        df = qualifying_df.copy()
        df.loc[0, "best_lap_seconds"] = 50.0
        with pytest.raises(pa.errors.SchemaErrors):
            QualifyingRawSchema.validate(df, lazy=True)
 
    def test_year_out_of_range_fails(self, qualifying_df):
        df = qualifying_df.copy()
        df.loc[0, "year"] = 2010
        with pytest.raises(pa.errors.SchemaErrors):
            QualifyingRawSchema.validate(df, lazy=True)



class TestResultsSchema:
 
    def test_valid_rows_pass(self, results_df):
        result = ResultsRawSchema.validate(results_df, lazy=True)
        assert len(result) == 2
 
    def test_grid_zero_allowed(self, results_df):
        df = results_df.copy()
        df.loc[0, "grid_position"] = 0
        result = ResultsRawSchema.validate(df, lazy=True)
        assert len(result) == 2
 
    def test_negative_points_fails(self, results_df):
        df = results_df.copy()
        df.loc[0, "points"] = -5.0
        with pytest.raises(pa.errors.SchemaErrors) as exc:
            ResultsRawSchema.validate(df, lazy=True)
        assert "points" in exc.value.failure_cases["column"].values
 
    def test_finish_position_zero_fails(self, results_df):
        df = results_df.copy()
        df.loc[0, "finish_position"] = 0
        with pytest.raises(pa.errors.SchemaErrors):
            ResultsRawSchema.validate(df, lazy=True)



class TestTelemetrySchema:
 
    def test_valid_rows_pass(self, telemetry_df):
        result = TelemetryRawSchema.validate(telemetry_df, lazy=True)
        assert len(result) == len(telemetry_df)
 
    def test_lap_seconds_nullable(self, telemetry_df):
        df = telemetry_df.copy()
        df.loc[0, "lap_seconds"] = None
        result = TelemetryRawSchema.validate(df, lazy=True)
        assert len(result) == len(telemetry_df)
 
    def test_invalid_compound_fails(self, telemetry_df):
        df = telemetry_df.copy()
        df.loc[0, "compound"] = "SUPERSOFT"
        with pytest.raises(pa.errors.SchemaErrors) as exc:
            TelemetryRawSchema.validate(df, lazy=True)
        assert "compound" in exc.value.failure_cases["column"].values
 
    def test_compound_nullable(self, telemetry_df):
        df = telemetry_df.copy()
        df.loc[0, "compound"] = None
        result = TelemetryRawSchema.validate(df, lazy=True)
        assert len(result) == len(telemetry_df)
 
    def test_lap_too_fast_fails(self, telemetry_df):
        df = telemetry_df.copy()
        df.loc[0, "lap_seconds"] = 45.0
        with pytest.raises(pa.errors.SchemaErrors):
            TelemetryRawSchema.validate(df, lazy=True)
 
    def test_lap_too_slow_fails(self, telemetry_df):
        df = telemetry_df.copy()
        df.loc[0, "lap_seconds"] = 400.0
        with pytest.raises(pa.errors.SchemaErrors):
            TelemetryRawSchema.validate(df, lazy=True)


# ---------------------------------------------------------------------------
# Repository — patched to use the test SQLite session
# ---------------------------------------------------------------------------
 
@pytest.fixture
def repo(session, monkeypatch):
    from contextlib import contextmanager
    r = RawDataRepository()
 
    @contextmanager
    def mock_get_session():
        yield session
 
    monkeypatch.setattr("app.db.repositories.raw_data_repo.get_session", mock_get_session)
    return r
 
 
class TestUpsertQualifying:
 
    def test_empty_returns_zero(self, repo):
        assert repo.upsert_qualifying(pd.DataFrame()) == 0
 
    def test_valid_rows_inserted(self, repo, session, qualifying_df):
        count = repo.upsert_qualifying(qualifying_df)
        assert count == 2
        rows = session.execute(
            text("SELECT driver_code FROM qualifying_raw ORDER BY position")
        ).fetchall()
        assert [r[0] for r in rows] == ["VER", "LEC"]
 
    def test_upsert_idempotent(self, repo, session, qualifying_df):
        repo.upsert_qualifying(qualifying_df)
        repo.upsert_qualifying(qualifying_df)
        count = session.execute(text("SELECT COUNT(*) FROM qualifying_raw")).scalar()
        assert count == 2
 
    def test_upsert_updates_field(self, repo, session, qualifying_df):
        repo.upsert_qualifying(qualifying_df)
        updated = qualifying_df.copy()
        updated.loc[0, "best_lap_seconds"] = 85.0
        repo.upsert_qualifying(updated)
        row = session.execute(
            text("SELECT best_lap_seconds FROM qualifying_raw WHERE driver_code='VER'")
        ).fetchone()
        assert abs(row[0] - 85.0) < 0.01
 
    def test_numpy_types_accepted(self, repo, qualifying_df):
        df = qualifying_df.copy()
        df["position"] = df["position"].astype(np.int64)
        df["best_lap_seconds"] = df["best_lap_seconds"].astype(np.float64)
        assert repo.upsert_qualifying(df) == 2
 
    def test_nan_stored_as_null(self, repo, session, qualifying_df):
        df = qualifying_df.copy()
        df.loc[0, "best_lap_seconds"] = float("nan")
        repo.upsert_qualifying(df)
        row = session.execute(
            text("SELECT best_lap_seconds FROM qualifying_raw WHERE driver_code='VER'")
        ).fetchone()
        assert row[0] is None
 
 
class TestUpsertResults:
 
    def test_valid_rows_inserted(self, repo, session, results_df):
        count = repo.upsert_results(results_df)
        assert count == 2
 
    def test_upsert_idempotent(self, repo, session, results_df):
        repo.upsert_results(results_df)
        repo.upsert_results(results_df)
        assert session.execute(text("SELECT COUNT(*) FROM results_raw")).scalar() == 2
 
    def test_empty_returns_zero(self, repo):
        assert repo.upsert_results(pd.DataFrame()) == 0
 
 
class TestUpsertTelemetry:
 
    def test_valid_rows_inserted(self, repo, session, telemetry_df):
        count = repo.upsert_telemetry(telemetry_df)
        assert count == len(telemetry_df)
 
    def test_upsert_idempotent(self, repo, session, telemetry_df):
        repo.upsert_telemetry(telemetry_df)
        repo.upsert_telemetry(telemetry_df)
        assert session.execute(text("SELECT COUNT(*) FROM telemetry_raw")).scalar() == len(telemetry_df)
 
    def test_null_lap_seconds_stored(self, repo, session, telemetry_df):
        df = telemetry_df.copy()
        df.loc[0, "lap_seconds"] = None
        repo.upsert_telemetry(df)
        row = session.execute(
            text("SELECT lap_seconds FROM telemetry_raw WHERE driver_code='VER' AND lap_number=1")
        ).fetchone()
        assert row[0] is None
 
 
class TestValidationFailure:
 
    def test_inserts_record(self, repo, session):
        repo.insert_validation_failure("qualifying_raw", "bahrain_2024", "position=25")
        count = session.execute(text("SELECT COUNT(*) FROM validation_failures")).scalar()
        assert count == 1
 
    def test_never_raises_on_db_error(self, monkeypatch):
        from contextlib import contextmanager
        r = RawDataRepository()
 
        @contextmanager
        def broken():
            raise Exception("DB down")
            yield
 
        monkeypatch.setattr("app.db.repositories.raw_data_repo.get_session", broken)
        r.insert_validation_failure("qualifying_raw", "bahrain_2024", "test")  # must not raise
 