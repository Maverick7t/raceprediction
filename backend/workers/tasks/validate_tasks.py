"""
Prefect validation tasks.
 
Validation is performed in lazy=True mode so ALL failures in a DataFrame
are collected before any action is taken.
 
Behaviour on failure:
  - Invalid rows are written to the validation_failures audit table.
  - Valid rows are returned and continue through the pipeline.
  - If ALL rows fail, a ValidationError is raised — the flow fails and alerts.
  - If SOME rows fail, the flow continues with the valid subset only.
 
This design means the pipeline never silently loses data.
You always know exactly what came in, what passed, and what didn't.
"""
 
import pandas as pd
import pandera as pa
from prefect import task
 
from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.repositories.raw_data_repo import RawDataRepository
from app.validation.qualifying_schema import QualifyingRawSchema
from app.validation.results_schema import ResultsRawSchema
from app.validation.telemetry_schema import TelemetryRawSchema
 
logger = get_logger(__name__)
_repo = RawDataRepository()
 
 
@task(name="validate_qualifying", description="Validate qualifying rows against Pandera schema")
def validate_qualifying(df: pd.DataFrame, race_key: str) -> pd.DataFrame:
    return _validate(df, QualifyingRawSchema, "qualifying_raw", race_key)

@task(name="validate_results", description="Validate race result rows against Pandera schema")
def validate_results(df: pd.DataFrame, race_key: str) -> pd.DataFrame:
    return _validate(df, ResultsRawSchema, "results_raw", race_key)
 
 
@task(name="validate_telemetry", description="Validate telemetry rows against Pandera schema")
def validate_telemetry(df: pd.DataFrame, race_key: str) -> pd.DataFrame:
    return _validate(df, TelemetryRawSchema, "telemetry_raw", race_key)