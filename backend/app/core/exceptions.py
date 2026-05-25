class F1PredictionError(Exception):
    """Base for all application errors. Never catch this — catch specific subtypes."""
    pass


class IngestionError(F1PredictionError):
    """
    Raised when data cannot be fetched from an external source after all retries.
    source: "fastf1" | "ergast" | "openf1"
    """
    def __init__(self, source: str, message: str):
        self.source = source
        super().__init__(f"[{source}] {message}")


class ValidationError(F1PredictionError):
    """
    Raised when an entire DataFrame fails schema validation and no valid rows remain.
    Individual row failures are logged to validation_failures table — they do not raise.
    """
    def __init__(self, table: str, failure_count: int, message: str):
        self.table = table
        self.failure_count = failure_count
        super().__init__(f"[{table}] {failure_count} rows failed validation: {message}")


class StorageError(F1PredictionError):
    """
    Raised when a Supabase write fails after the repository layer has handled retries.
    table: the Supabase table name where the write was attempted.
    """
    def __init__(self, table: str, message: str):
        self.table = table
        super().__init__(f"[{table}] storage error: {message}")