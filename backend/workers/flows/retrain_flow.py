"""
workers/flows/retrain_flow.py
 
Triggered automatically by post_race_flow after every race.
 
Flow steps:
  1. Check if retraining condition is met (≥3 new results)
  2. If not → exit early, log skip
  3. If yes → run full training pipeline
  4. Evaluate new model vs production
  5. Promote if metrics improve sufficiently
  6. Log everything to MLflow
 
This flow never crashes the API.
If training fails, the existing production model continues serving.
"""
 
from prefect import flow, task, get_run_logger
from app.core.sentry import init_sentry, set_sentry_context
 
from app.ml.training.evaluator import should_retrain, should_promote, promote_model
from app.ml.training.trainer import retrain_from_supabase
 
 
@task(name="check_retrain_trigger")
def check_trigger_task() -> bool:
    return should_retrain()
 
 
@task(name="run_training", retries=1, retry_delay_seconds=60)
def run_training_task() -> dict:
    return retrain_from_supabase()
 
 
@task(name="evaluate_and_promote")
def evaluate_task(metrics: dict) -> dict:
    promote, reason = should_promote(metrics)
    run_id = metrics.get("run_id", "unknown")
 
    if promote:
        promote_model(metrics, run_id)
        return {"promoted": True, "reason": reason, "run_id": run_id}
    else:
        return {"promoted": False, "reason": reason, "run_id": run_id}
 
 
@flow(name="retrain_flow", log_prints=True)
def retrain_flow() -> dict:
    init_sentry()
    set_sentry_context(flow_name="retrain_flow")
    logger = get_run_logger()


    # Step 1: Check trigger condition
    trigger = check_trigger_task()
 
    if not trigger:
        logger.info("Retrain condition not met — skipping")
        return {"status": "skipped", "reason": "fewer than 3 new results"}
 
    logger.info("Retrain condition met — starting training pipeline")
 
    # Step 2: Train
    try:
        metrics = run_training_task()
    except Exception as e:
        logger.error(f"Training failed: {e}")
        return {"status": "failed", "error": str(e)}
 
    logger.info(f"Training complete: {metrics}")
 
    # Step 3: Evaluate and promote
    promotion_result = evaluate_task(metrics)
 
    logger.info(f"Promotion decision: {promotion_result}")
 
    return {
        "status": "completed",
        "metrics": metrics,
        "promotion": promotion_result,
    }
 
 
if __name__ == "__main__":
    result = retrain_flow()
    print(result)