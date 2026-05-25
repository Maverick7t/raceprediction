"""
app/validation/schemas.py
 
All Pandera DataFrame schemas for Phase 1 raw tables.
Imported by validate_tasks.py (Prefect) and test_validation.py (pytest).
"""
 
import pandera as pa
from pandera import Check, Column, DataFrameSchema
 
_VALID_COMPOUNDS = {"SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"}
 
 
QualifyingRawSchema = DataFrameSchema(
    columns={
        "driver_code": Column(str, Check(lambda s: s.str.len().between(2, 4)), nullable=False),
        "driver_id": Column(str, nullable=False),
        "driver_name": Column(str, nullable=False),
        "team": Column(str, nullable=False),
        "team_id": Column(str, nullable=False),
        "position": Column(int, Check.in_range(1, 20), nullable=False),
        "q1_time": Column(str, nullable=True),
        "q2_time": Column(str, nullable=True),
        "q3_time": Column(str, nullable=True),
        "best_lap_seconds": Column(
            float,
            checks=[Check.greater_than(60.0), Check.less_than(200.0)],
            nullable=True,
        ),
        "year": Column(int, Check.in_range(2018, 2035), nullable=False),
        "round": Column(int, Check.in_range(1, 25), nullable=False),
        "race_key": Column(str, Check(lambda s: s.str.len() >= 5), nullable=False),
        "race_name": Column(str, nullable=False),
        "circuit_id": Column(str, nullable=False),
        "source": Column(str, nullable=False),
    },
    strict=False,
    coerce=True,
)