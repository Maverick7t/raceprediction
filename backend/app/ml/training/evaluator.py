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


def should_retrain() -> bool:
    """
    Returns True if ≥3 new results_raw rows have been ingested
    since the last recorded training run.
 
    'Last training run' is determined by reading the trained_at timestamp
    from models/metadata.json. If no metadata exists, always returns True.
    """
    last_trained_at = _get_last_trained_at()
 
    if last_trained_at is None:
        logger.info("No previous training run found — retraining required")
        return True
 
    try:
        with get_session() as session:
            count = session.execute(text("""
                SELECT COUNT(*) FROM results_raw
                WHERE ingested_at > :last_trained
            """), {"last_trained": last_trained_at}).scalar()
 
        new_results = count or 0
        logger.info(f"New results since last training: {new_results}")
 
        if new_results >= 3:
            logger.info("Retraining trigger: ≥3 new results — will retrain")
            return True
        else:
            logger.info(f"Retraining skipped: only {new_results} new results (need 3)")
            return False
 
    except Exception as e:
        logger.error(f"should_retrain check failed: {e}")
        return False
    
    def should_promote(new_metrics: dict) -> tuple[bool, str]:
    """
    Compare new model metrics against current production model metrics.
 
    Returns:
      (True, reason)  — promote the new model
      (False, reason) — keep current production model
 
    Args:
      new_metrics: dict with winner_top3_accuracy, winner_exact_accuracy, podium_accuracy
    """
    # Check minimum absolute thresholds first
    for metric, threshold in MINIMUM_THRESHOLDS.items():
        if new_metrics.get(metric, 0) < threshold:
            reason = (
                f"New model failed minimum threshold: "
                f"{metric}={new_metrics.get(metric, 0):.4f} < {threshold}"
            )
            logger.warning(reason)
            return False, reason
 
    # Load current production metrics
    current_metrics = _get_production_metrics()
 
    if current_metrics is None:
        reason = "No production model exists — promoting new model automatically"
        logger.info(reason)
        return True, reason
 
    # Count how many metrics the new model beats by the required margin
    metrics_beaten = 0
    detail = []
 
    for metric in ["winner_top3_accuracy", "winner_exact_accuracy", "podium_accuracy"]:
        new_val = new_metrics.get(metric, 0)
        current_val = current_metrics.get(metric, 0)
        required_improvement = PROMOTION_RULES[metric]
        improvement = new_val - current_val
 
        if improvement >= required_improvement:
            metrics_beaten += 1
            detail.append(f"{metric}: {current_val:.4f} → {new_val:.4f} (+{improvement:.4f}) ✓")
        else:
            detail.append(f"{metric}: {current_val:.4f} → {new_val:.4f} ({improvement:+.4f}) ✗")
 
    detail_str = ", ".join(detail)
 
    if metrics_beaten >= PROMOTION_RULES["min_metrics_to_beat"]:
        reason = f"New model beats production on {metrics_beaten}/3 metrics. {detail_str}"
        logger.info(f"PROMOTE: {reason}")
        return True, reason
    else:
        reason = (
            f"New model only beats production on {metrics_beaten}/3 metrics "
            f"(need {PROMOTION_RULES['min_metrics_to_beat']}). {detail_str}"
        )
        logger.warning(f"NO PROMOTE: {reason}")
        return False, reason