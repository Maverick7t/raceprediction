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
from app.db.repositories.raw_data_repo import RawDataRepository
from app.validation.schemas import QualifyingRawSchema, ResultsRawSchema, TelemetryRawSchema
 
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


# ------------------------------------------------------------------
# Internal
# ------------------------------------------------------------------
 
def _validate(
    df: pd.DataFrame,
    schema,
    table_name: str,
    race_key: str,
) -> pd.DataFrame:
    """
    Core validation logic shared by all three validation tasks.
 
    1. Run Pandera schema in lazy mode — collect all failures.
    2. Log each failure to the validation_failures audit table.
    3. Drop failed rows, return valid rows only.
    4. Raise ValidationError if no valid rows remain.
    """
    if df is None or df.empty:
        logger.warning(f"validate called with empty DataFrame for {table_name}")
        raise ValidationError(table_name, 0, "Input DataFrame is empty")
 
    try:
        validated_df = schema.validate(df, lazy=True)
        logger.info(
            f"Validation passed: table={table_name} race_key={race_key} "
            f"rows={len(validated_df)}"
        )
        return validated_df
 
    except pa.errors.SchemaErrors as exc:
        failure_cases = exc.failure_cases
        failed_indices = set(
            failure_cases["index"].dropna().astype(int).tolist()
        )
        failure_count = len(failed_indices)
        total = len(df)
 
        logger.warning(
            f"Validation: {failure_count}/{total} rows failed "
            f"table={table_name} race_key={race_key}"
        )
 
        # Write each failure to audit log — non-fatal
        for _, row in failure_cases.iterrows():
            _repo.insert_validation_failure(
                table=table_name,
                race_key=race_key,
                failure_reason=(
                    f"column={row['column']} "
                    f"check={row['check']} "
                    f"value={row['failure_case']}"
                ),
            )
 
        valid_df = df.drop(index=list(failed_indices)).reset_index(drop=True)
 
        if valid_df.empty:
            raise ValidationError(
                table_name,
                failure_count,
                f"All {total} rows failed validation for race_key={race_key}",
            )
 
        logger.info(
            f"Returning {len(valid_df)} valid rows after filtering "
            f"{failure_count} failures for {table_name}"
        )
        return valid_df
 