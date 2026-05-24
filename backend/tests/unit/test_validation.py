"""
Unit tests for Pandera validation schemas.
 
Tests cover:
  - Valid rows pass without modification
  - Individual invalid values are caught (position out of range, wrong driver code length, etc.)
  - Nullable fields accept None without failing
  - The _validate helper returns valid rows and drops invalid ones
"""
 
import pandas as pd
import pandera as pa
import pytest
 
from app.validation.qualifying_schema import QualifyingRawSchema
from app.validation.results_schema import ResultsRawSchema
from app.validation.telemetry_schema import TelemetryRawSchema
 
 
# ---------------------------------------------------------------------------
# QualifyingRawSchema
# ---------------------------------------------------------------------------
 
class TestQualifyingSchema:
 
    def test_valid_rows_pass(self, valid_qualifying_df):
        result = QualifyingRawSchema.validate(valid_qualifying_df, lazy=True)
        assert len(result) == len(valid_qualifying_df)
 
    def test_position_out_of_range_fails(self, valid_qualifying_df):
        df = valid_qualifying_df.copy()
        df.loc[0, "position"] = 25  # Invalid: max is 20
        with pytest.raises(pa.errors.SchemaErrors) as exc_info:
            QualifyingRawSchema.validate(df, lazy=True)
        failures = exc_info.value.failure_cases
        assert "position" in failures["column"].values
 
    def test_q2_q3_nullable(self, valid_qualifying_df):
        """Drivers eliminated in Q1 have null Q2 and Q3 times."""
        df = valid_qualifying_df.copy()
        df.loc[0, "q2_time"] = None
        df.loc[0, "q3_time"] = None
        result = QualifyingRawSchema.validate(df, lazy=True)
        assert len(result) == 2
 
    def test_best_lap_seconds_nullable(self, valid_qualifying_df):
        """best_lap_seconds is null when FastF1 enrichment is unavailable."""
        df = valid_qualifying_df.copy()
        df["best_lap_seconds"] = None
        result = QualifyingRawSchema.validate(df, lazy=True)
        assert len(result) == 2
 
    def test_best_lap_too_fast_fails(self, valid_qualifying_df):
        df = valid_qualifying_df.copy()
        df.loc[0, "best_lap_seconds"] = 50.0  # Under 60s — physically impossible
        with pytest.raises(pa.errors.SchemaErrors):
            QualifyingRawSchema.validate(df, lazy=True)
 
    def test_year_out_of_range_fails(self, valid_qualifying_df):
        df = valid_qualifying_df.copy()
        df.loc[0, "year"] = 2010  # Before 2018 cutoff
        with pytest.raises(pa.errors.SchemaErrors):
            QualifyingRawSchema.validate(df, lazy=True)