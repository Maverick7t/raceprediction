"""
Unit tests — RawDataRepository (SQLAlchemy + SQLite in-memory).
 
WHEN TO RUN:
  After writing/changing app/db/repositories/raw_data_repo.py
    pytest tests/unit/test_raw_data_repo.py -v
  CI: runs on every push automatically.
 
No credentials needed. No network. Pure SQLite.
"""
 
import numpy as np
 
from app.db.repositories.raw_data_repo import _to_python_type
 
 
# ------_to_python_type ---------------------------------------------------------------------------
 
class TestToPythonType:
    def test_numpy_int64(self):
        assert _to_python_type(np.int64(42)) == 42
        assert type(_to_python_type(np.int64(42))) is int
 
    def test_numpy_float64(self):
        assert abs(_to_python_type(np.float64(3.14)) - 3.14) < 0.001
 
    def test_numpy_nan_returns_none(self):
        assert _to_python_type(np.float64("nan")) is None
 
    def test_python_float_nan_returns_none(self):
        assert _to_python_type(float("nan")) is None
 
    def test_none_stays_none(self):
        assert _to_python_type(None) is None
 
    def test_numpy_bool(self):
        assert _to_python_type(np.bool_(True)) is True
        assert type(_to_python_type(np.bool_(True))) is bool