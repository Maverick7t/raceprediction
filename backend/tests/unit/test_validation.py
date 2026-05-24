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