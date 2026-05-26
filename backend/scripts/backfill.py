"""
scripts/backfill.py
 
One-time backfill script. Ingests all race results + qualifying
from 2018 to the specified end year, then computes features for each race.
 
Run once before Phase 3 training:
  python -m scripts.backfill --from-year 2018 --to-year 2024
 
This will:
  1. For each season/round: fetch qualifying + race results from Ergast
  2. Validate and store in raw tables
  3. Compute features for each race (with proper rolling windows)
  4. Store in features_by_race
 
FastF1 telemetry is skipped during backfill — it's too slow for 7 seasons.
Telemetry is only fetched for live race weekends going forward.
 
Time estimate: ~45-90 minutes for 2018-2024 (Ergast rate limits).
"""
 
import argparse
import time
 
from app.integrations.ergast import ErgastClient
from app.db.repositories.raw_data_repo import RawDataRepository
from app.validation.schemas import QualifyingRawSchema, ResultsRawSchema
from app.features.compute import compute_features_for_race
from app.db.repositories.feature_repo import FeatureRepository
from app.core.logging import get_logger
 
logger = get_logger(__name__)
 
_ergast = ErgastClient()
_raw_repo = RawDataRepository()
_feature_repo = FeatureRepository()
 
# Rounds per season — conservative upper bound
MAX_ROUNDS = 24
 
# Delay between Ergast requests to avoid rate limiting
REQUEST_DELAY = 1.5  # seconds

def backfill(from_year: int = 2018, to_year: int = 2024) -> None:
    logger.info(f"Backfill started from_year={from_year} to_year={to_year}")
 
    total_qualifying = 0
    total_results = 0
    total_features = 0
    failed_rounds = []
 
    for year in range(from_year, to_year + 1):
        logger.info(f"Processing season {year}")
 
        # Fetch season schedule to know how many rounds
        try:
            schedule = _ergast.get_driver_standings(year)
            # Use standings to determine last completed round
            # If empty, skip year
            if schedule.empty:
                logger.warning(f"No standings data for {year} — skipping")
                continue
        except Exception as e:
            logger.error(f"Could not fetch standings for {year}: {e}")
            continue
 
        for round_number in range(1, MAX_ROUNDS + 1):
            race_key = None
            try:
                # --- Qualifying ---
                time.sleep(REQUEST_DELAY)
                quali_df = _ergast.get_qualifying_results(year, round_number)
 
                if quali_df.empty:
                    logger.info(f"No qualifying data for {year} R{round_number} — end of season")
                    break
 
                race_key = quali_df["race_key"].iloc[0]
 
                # Validate
                try:
                    validated_quali = QualifyingRawSchema.validate(quali_df, lazy=True)
                except Exception as e:
                    logger.warning(f"Qualifying validation partial failure {year} R{round_number}: {e}")
                    validated_quali = quali_df  # proceed with raw data
 
                _raw_repo.upsert_qualifying(validated_quali)
                total_qualifying += len(validated_quali)
                logger.info(f"Qualifying stored: {year} R{round_number} {race_key}")
 
                # --- Race results ---
                time.sleep(REQUEST_DELAY)
                results_df = _ergast.get_race_results(year, round_number)
 
                if not results_df.empty:
                    try:
                        validated_results = ResultsRawSchema.validate(results_df, lazy=True)
                    except Exception as e:
                        logger.warning(f"Results validation partial failure {year} R{round_number}: {e}")
                        validated_results = results_df
 
                    _raw_repo.upsert_results(validated_results)
                    total_results += len(validated_results)
                    logger.info(f"Results stored: {year} R{round_number} {race_key}")
 
                # --- Features ---
                features_df = compute_features_for_race(race_key, year, round_number)
                if not features_df.empty:
                    _feature_repo.upsert_features(features_df)
                    total_features += len(features_df)
 
                logger.info(
                    f"Round complete: {year} R{round_number} "
                    f"quali={len(validated_quali)} "
                    f"results={len(results_df) if not results_df.empty else 0} "
                    f"features={len(features_df)}"
                )
 
            except Exception as e:
                logger.error(f"Failed {year} R{round_number} race_key={race_key}: {e}")
                failed_rounds.append({"year": year, "round": round_number, "error": str(e)})
                # Continue with next round — don't abort the whole backfill
                continue
 
    logger.info(
        f"Backfill complete: "
        f"qualifying_rows={total_qualifying} "
        f"results_rows={total_results} "
        f"feature_rows={total_features} "
        f"failed_rounds={len(failed_rounds)}"
    )
 
    if failed_rounds:
        logger.warning(f"Failed rounds: {failed_rounds}")
 
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill F1 historical data")
    parser.add_argument("--from-year", type=int, default=2018)
    parser.add_argument("--to-year", type=int, default=2024)
    args = parser.parse_args()
    backfill(from_year=args.from_year, to_year=args.to_year)
 