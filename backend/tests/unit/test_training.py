"""
Unit tests — Phase 3 ML training.
 
WHEN TO RUN:
  After writing/changing trainer.py or evaluator.py
    pytest tests/unit/test_training.py -v
  CI: runs when files under app/ml/ change.
 
No real training happens in these tests.
No database calls. No MLflow calls.
All external dependencies are mocked.
"""
 
import json
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
 
from app.ml.training.evaluator import should_promote, PROMOTION_RULES, MINIMUM_THRESHOLDS
from app.ml.training.trainer import (
    _encode_and_clean,
    _evaluate,
    FEATURE_COLUMNS,
    CATEGORICAL_COLUMNS,
)