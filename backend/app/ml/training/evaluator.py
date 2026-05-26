"""
app/ml/training/evaluator.py
 
Two responsibilities:
  1. Retraining trigger — should we retrain right now?
  2. Model promotion — should the new model replace production?
 
Retraining trigger rule:
  Retrain if ≥3 new results_raw rows exist since the last training run.
  This means retraining happens ~every 3 races during the season.
  Never during off-season. Never on a fixed schedule.
 
Promotion rule:
  New model must beat current production model by MIN_IMPROVEMENT
  on at least 2 out of 3 key metrics.
  If condition not met: log as candidate in MLflow, keep current production.
"""
 
import json
from pathlib import Path
 
from app.core.logging import get_logger
from app.db.session import get_session
from sqlalchemy import text
 
logger = get_logger(__name__)
 
MODELS_DIR = Path("models")
 
# Minimum improvement required over production model to trigger promotion
PROMOTION_RULES = {
    "winner_top3_accuracy":   0.02,   # must improve by 2 percentage points
    "winner_exact_accuracy":  0.02,
    "podium_accuracy":        0.02,
    "min_metrics_to_beat":    2,       # must beat production on at least 2 of 3
}
 
# Minimum acceptable absolute accuracy (even if better than production)
MINIMUM_THRESHOLDS = {
    "winner_top3_accuracy":  0.30,    # must get actual winner in top 3 at least 30% of time
    "winner_exact_accuracy": 0.10,    # exact winner correct at least 10% of time
    "podium_accuracy":       0.50,    # podium binary correct at least 50% of time
}