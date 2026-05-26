"""
app/features/compute.py
 
Feature computation engine.
Reads from raw tables, computes all features, returns a DataFrame
ready to be written to features_by_race.
 
Rules:
  - Never called during an API request — offline only
  - All rolling calculations use only past races (no data leakage)
  - Missing data produces None, never crashes
  - One function per feature group for testability
 
Circuit features are static lookup values — they don't change race to race.
Driver/team features are rolling — they update after every race.
Session features come from qualifying — computed after Saturday qualifying.
"""
 
import pandas as pd
import numpy as np
from sqlalchemy import text
 
from app.core.logging import get_logger
from app.db.session import get_session
 
logger = get_logger(__name__)
 

# ---------------------------------------------------------------------------
# Static circuit data
# Overtaking difficulty: 1.0 = very easy (Monza), 10.0 = very hard (Monaco)
# Tire deg factor: 1.0 = low deg, 10.0 = high deg
# Safety car probability: 0.0 to 1.0 based on historical frequency
# ---------------------------------------------------------------------------
CIRCUIT_FEATURES: dict[str, dict] = {
    "bahrain":          {"overtaking_difficulty": 4.0, "tire_deg_factor": 7.0, "safety_car_probability": 0.35},
    "jeddah":           {"overtaking_difficulty": 5.0, "tire_deg_factor": 5.0, "safety_car_probability": 0.55},
    "albert_park":      {"overtaking_difficulty": 5.0, "tire_deg_factor": 4.0, "safety_car_probability": 0.45},
    "suzuka":           {"overtaking_difficulty": 3.0, "tire_deg_factor": 6.0, "safety_car_probability": 0.30},
    "shanghai":         {"overtaking_difficulty": 5.0, "tire_deg_factor": 5.0, "safety_car_probability": 0.40},
    "miami":            {"overtaking_difficulty": 5.0, "tire_deg_factor": 6.0, "safety_car_probability": 0.50},
    "imola":            {"overtaking_difficulty": 3.0, "tire_deg_factor": 4.0, "safety_car_probability": 0.35},
    "monaco":           {"overtaking_difficulty": 9.5, "tire_deg_factor": 2.0, "safety_car_probability": 0.65},
    "villeneuve":       {"overtaking_difficulty": 4.0, "tire_deg_factor": 3.0, "safety_car_probability": 0.40},
    "catalunya":        {"overtaking_difficulty": 3.0, "tire_deg_factor": 7.0, "safety_car_probability": 0.25},
    "red_bull_ring":    {"overtaking_difficulty": 4.0, "tire_deg_factor": 5.0, "safety_car_probability": 0.40},
    "silverstone":      {"overtaking_difficulty": 4.0, "tire_deg_factor": 6.0, "safety_car_probability": 0.30},
    "hungaroring":      {"overtaking_difficulty": 3.0, "tire_deg_factor": 5.0, "safety_car_probability": 0.30},
    "spa":              {"overtaking_difficulty": 5.0, "tire_deg_factor": 4.0, "safety_car_probability": 0.45},
    "zandvoort":        {"overtaking_difficulty": 2.0, "tire_deg_factor": 6.0, "safety_car_probability": 0.35},
    "monza":            {"overtaking_difficulty": 7.0, "tire_deg_factor": 2.0, "safety_car_probability": 0.40},
    "baku":             {"overtaking_difficulty": 7.0, "tire_deg_factor": 3.0, "safety_car_probability": 0.65},
    "marina_bay":       {"overtaking_difficulty": 3.0, "tire_deg_factor": 3.0, "safety_car_probability": 0.65},
    "americas":         {"overtaking_difficulty": 5.0, "tire_deg_factor": 6.0, "safety_car_probability": 0.40},
    "rodriguez":        {"overtaking_difficulty": 4.0, "tire_deg_factor": 4.0, "safety_car_probability": 0.35},
    "interlagos":       {"overtaking_difficulty": 6.0, "tire_deg_factor": 4.0, "safety_car_probability": 0.55},
    "vegas":            {"overtaking_difficulty": 6.0, "tire_deg_factor": 3.0, "safety_car_probability": 0.45},
    "losail":           {"overtaking_difficulty": 4.0, "tire_deg_factor": 7.0, "safety_car_probability": 0.30},
    "yas_marina":       {"overtaking_difficulty": 5.0, "tire_deg_factor": 4.0, "safety_car_probability": 0.30},
}
 
_DEFAULT_CIRCUIT = {"overtaking_difficulty": 5.0, "tire_deg_factor": 5.0, "safety_car_probability": 0.40}
 
DNF_STATUSES = {
    "Accident", "Collision", "Engine", "Gearbox", "Hydraulics",
    "Mechanical", "Power Unit", "Suspension", "Transmission",
    "Brakes", "Electrical", "Oil leak", "Puncture", "Retired",
    "Wheel", "Fire", "Cooling", "Fuel system",
}
 
WINDOW = 5  # rolling window size


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
 
def compute_features_for_race(
    race_key: str,
    year: int,
    round_number: int,
) -> pd.DataFrame:
    """
    Compute all features for every driver in a given race.
 
    Called twice per race weekend:
      1. After qualifying (Saturday) — session features available,
         finish_position/is_winner/is_podium are None (race hasn't happened)
      2. After race (Sunday) — targets filled in
 
    Returns one row per driver ready for features_by_race upsert.
    """
    logger.info(f"Computing features race_key={race_key} year={year} round={round_number}")
 
    qualifying_df = _load_qualifying(race_key)
    results_history = _load_results_history(year, round_number)
    quali_history = _load_qualifying_history(year, round_number)
    current_results = _load_current_results(race_key)
    telemetry_df = _load_telemetry(race_key)
 
    if qualifying_df.empty:
        logger.error(f"No qualifying data found for race_key={race_key}")
        return pd.DataFrame()
 
    rows = []
 
    for _, driver_row in qualifying_df.iterrows():
        driver_code = driver_row["driver_code"]
        team_id = driver_row["team_id"]
 
        driver_results = results_history[results_history["driver_code"] == driver_code]
        driver_quali = quali_history[quali_history["driver_code"] == driver_code]
        team_results = results_history[results_history["team_id"] == team_id]
        driver_telemetry = telemetry_df[telemetry_df["driver_code"] == driver_code]
 
        # --- Driver features ---
        avg_finish = _avg_finish(driver_results)
        avg_quali = _avg_quali(driver_quali)
        podium_rate = _podium_rate(driver_results)
        dnf_rate = _dnf_rate(driver_results)
        wet_score = _wet_weather_score(driver_results)
        teammate_delta = _teammate_delta(driver_code, team_id, quali_history)
        tire_mgmt = _tire_management_score(driver_telemetry)
 
        # --- Team features ---
        constructor_form = _constructor_form(team_results)
        pitstop_avg = _pitstop_avg(driver_telemetry)
        reliability = _reliability_score(team_results)
 
        # --- Circuit features ---
        circuit_id = driver_row["circuit_id"]
        circuit = CIRCUIT_FEATURES.get(circuit_id, _DEFAULT_CIRCUIT)
 
        # --- Session features ---
        quali_pos = int(driver_row["position"])
        pole_time = qualifying_df["best_lap_seconds"].min()
        driver_time = driver_row.get("best_lap_seconds")
        quali_delta = (
            round(float(driver_time) - float(pole_time), 3)
            if pd.notna(driver_time) and pd.notna(pole_time) and pole_time > 0
            else None
        )
 
        # --- Targets (only available after race) ---
        finish_pos = None
        is_winner = None
        is_podium = None
 
        if not current_results.empty:
            driver_result = current_results[current_results["driver_code"] == driver_code]
            if not driver_result.empty:
                fp = int(driver_result.iloc[0]["finish_position"])
                finish_pos = fp
                is_winner = 1 if fp == 1 else 0
                is_podium = 1 if fp <= 3 else 0
 
        rows.append({
            "race_key": race_key,
            "driver_code": driver_code,
            "driver_name": driver_row["driver_name"],
            "team_id": team_id,
            "year": year,
            "round": round_number,
            "circuit_id": circuit_id,
            "feature_version": "v1",
            # driver
            "avg_finish_last_5": avg_finish,
            "avg_quali_last_5": avg_quali,
            "podium_rate": podium_rate,
            "dnf_rate": dnf_rate,
            "wet_weather_score": wet_score,
            "teammate_delta": teammate_delta,
            "tire_management_score": tire_mgmt,
            # team
            "constructor_form": constructor_form,
            "pitstop_avg": pitstop_avg,
            "reliability_score": reliability,
            # circuit
            "overtaking_difficulty": circuit["overtaking_difficulty"],
            "tire_deg_factor": circuit["tire_deg_factor"],
            "safety_car_probability": circuit["safety_car_probability"],
            # session
            "qualifying_position": quali_pos,
            "qualifying_delta_to_pole": quali_delta,
            # targets
            "finish_position": finish_pos,
            "is_winner": is_winner,
            "is_podium": is_podium,
        })
 
    df = pd.DataFrame(rows)
    logger.info(f"Computed {len(df)} feature rows for race_key={race_key}")
    return df


# ---------------------------------------------------------------------------
# Data loaders — read from raw tables via SQLAlchemy
# ---------------------------------------------------------------------------
 
def _load_qualifying(race_key: str) -> pd.DataFrame:
    with get_session() as session:
        result = session.execute(text("""
            SELECT driver_code, driver_name, team_id, circuit_id,
                   position, best_lap_seconds, year, round
            FROM qualifying_raw
            WHERE race_key = :race_key
            ORDER BY position ASC
        """), {"race_key": race_key})
        rows = result.mappings().all()
    return pd.DataFrame(rows, columns=[
        "driver_code", "driver_name", "team_id", "circuit_id",
        "position", "best_lap_seconds", "year", "round",
    ])
 
 
def _load_results_history(year: int, round_number: int) -> pd.DataFrame:
    """Load all results BEFORE this race — no leakage."""
    with get_session() as session:
        result = session.execute(text("""
            SELECT driver_code, team_id, finish_position, points, status, year, round
            FROM results_raw
            WHERE (year < :year) OR (year = :year AND round < :round)
            ORDER BY year ASC, round ASC
        """), {"year": year, "round": round_number})
        rows = result.mappings().all()
    return pd.DataFrame(rows, columns=[
        "driver_code", "team_id", "finish_position", "points", "status", "year", "round",
    ])
 
 
def _load_qualifying_history(year: int, round_number: int) -> pd.DataFrame:
    """Load all qualifying results BEFORE this race."""
    with get_session() as session:
        result = session.execute(text("""
            SELECT driver_code, team_id, position, best_lap_seconds, year, round
            FROM qualifying_raw
            WHERE (year < :year) OR (year = :year AND round < :round)
            ORDER BY year ASC, round ASC
        """), {"year": year, "round": round_number})
        rows = result.mappings().all()
    return pd.DataFrame(rows, columns=[
        "driver_code", "team_id", "position", "best_lap_seconds", "year", "round",
    ])
 
 
def _load_current_results(race_key: str) -> pd.DataFrame:
    """Load race results for the current race (only available after Sunday)."""
    with get_session() as session:
        result = session.execute(text("""
            SELECT driver_code, finish_position, status
            FROM results_raw
            WHERE race_key = :race_key
        """), {"race_key": race_key})
        rows = result.mappings().all()
    return pd.DataFrame(rows, columns=["driver_code", "finish_position", "status"])
 
 
def _load_telemetry(race_key: str) -> pd.DataFrame:
    with get_session() as session:
        result = session.execute(text("""
            SELECT driver_code, lap_number, lap_seconds, stint,
                   compound, tyre_life, is_accurate
            FROM telemetry_raw
            WHERE race_key = :race_key
        """), {"race_key": race_key})
        rows = result.mappings().all()
    return pd.DataFrame(rows, columns=[
        "driver_code", "lap_number", "lap_seconds", "stint",
        "compound", "tyre_life", "is_accurate",
    ])


# ---------------------------------------------------------------------------
# Feature computation functions — one per feature, independently testable
# ---------------------------------------------------------------------------
 
def _avg_finish(driver_results: pd.DataFrame) -> float | None:
    """Average finish position over last WINDOW races."""
    if driver_results.empty:
        return None
    last = driver_results.tail(WINDOW)
    finished = last[~last["status"].isin(DNF_STATUSES)]
    if finished.empty:
        return None
    return round(float(finished["finish_position"].mean()), 3)
 
 
def _avg_quali(driver_quali: pd.DataFrame) -> float | None:
    """Average qualifying position over last WINDOW races."""
    if driver_quali.empty:
        return None
    last = driver_quali.tail(WINDOW)
    return round(float(last["position"].mean()), 3)
 
 
def _podium_rate(driver_results: pd.DataFrame) -> float | None:
    """Fraction of last WINDOW races where driver finished on podium."""
    if driver_results.empty:
        return None
    last = driver_results.tail(WINDOW)
    podiums = (last["finish_position"] <= 3).sum()
    return round(float(podiums / len(last)), 3)
 
 
def _dnf_rate(driver_results: pd.DataFrame) -> float | None:
    """Fraction of last WINDOW races where driver DNF'd."""
    if driver_results.empty:
        return None
    last = driver_results.tail(WINDOW)
    dnfs = last["status"].isin(DNF_STATUSES).sum()
    return round(float(dnfs / len(last)), 3)
 
 
def _wet_weather_score(driver_results: pd.DataFrame) -> float | None:
    """
    Proxy wet weather score — average points in races at known wet circuits.
    Real implementation would filter by actual weather data.
    For v1, we use Spa, Silverstone, Interlagos as wet-prone proxies.
    Returns None if no data at these circuits.
    """
    if driver_results.empty:
        return None
    # No circuit_id in results history — return neutral score for v1
    # Phase 2 enhancement: join with qualifying_raw to get circuit_id
    return 5.0
 
 
def _teammate_delta(
    driver_code: str,
    team_id: str,
    quali_history: pd.DataFrame,
) -> float | None:
    """
    Average qualifying position delta vs teammate over last WINDOW races.
    Negative = driver qualifies ahead of teammate (good).
    """
    if quali_history.empty:
        return None
 
    team_quali = quali_history[quali_history["team_id"] == team_id].copy()
    if team_quali.empty:
        return None
 
    # Get last WINDOW rounds this team appeared in
    rounds = team_quali[["year", "round"]].drop_duplicates().tail(WINDOW)
    if rounds.empty:
        return None
 
    deltas = []
    for _, r in rounds.iterrows():
        round_data = team_quali[
            (team_quali["year"] == r["year"]) &
            (team_quali["round"] == r["round"])
        ]
        if len(round_data) < 2:
            continue
        driver_pos = round_data[round_data["driver_code"] == driver_code]["position"]
        teammate_pos = round_data[round_data["driver_code"] != driver_code]["position"]
        if driver_pos.empty or teammate_pos.empty:
            continue
        deltas.append(float(driver_pos.iloc[0]) - float(teammate_pos.iloc[0]))
 
    if not deltas:
        return None
    return round(float(np.mean(deltas)), 3)
 
 
def _tire_management_score(driver_telemetry: pd.DataFrame) -> float | None:
    """
    Tire management score — how well pace is maintained in late stint.
    Computed as: (avg lap time in laps 1-5 of stint) / (avg lap time in last 5 laps of stint)
    Score > 1.0 means degrading, < 1.0 means improving.
    Lower is better for tire management (less degradation).
    Only uses accurate laps.
    """
    if driver_telemetry.empty:
        return None
 
    accurate = driver_telemetry[
        (driver_telemetry["is_accurate"] == True) &
        (driver_telemetry["lap_seconds"].notna())
    ]
    if accurate.empty:
        return None
 
    try:
        early_laps = accurate.groupby("stint").apply(
            lambda g: g.nsmallest(5, "tyre_life")["lap_seconds"].mean()
        )
        late_laps = accurate.groupby("stint").apply(
            lambda g: g.nlargest(5, "tyre_life")["lap_seconds"].mean()
        )
        if early_laps.empty or late_laps.empty:
            return None
        ratio = float((late_laps / early_laps).mean())
        return round(ratio, 4)
    except Exception:
        return None
 
 
def _constructor_form(team_results: pd.DataFrame) -> float | None:
    """Rolling average points per race for the constructor over last WINDOW races."""
    if team_results.empty:
        return None
    last = team_results.tail(WINDOW * 2)  # 2 drivers × WINDOW races
    if last.empty:
        return None
    points_by_round = last.groupby(["year", "round"])["points"].sum()
    return round(float(points_by_round.tail(WINDOW).mean()), 3)
 
 
def _pitstop_avg(driver_telemetry: pd.DataFrame) -> float | None:
    """
    Proxy pit stop duration — average stint transition lap time delta.
    Real pit stop data would come from OpenF1 in Phase 2 enhancement.
    For v1, return None (will be enhanced when OpenF1 pit data is stored).
    """
    return None
 
 
def _reliability_score(team_results: pd.DataFrame) -> float | None:
    """
    Constructor reliability — inverse of team DNF rate over last WINDOW*2 race entries.
    1.0 = perfectly reliable, 0.0 = DNF every race.
    """
    if team_results.empty:
        return None
    last = team_results.tail(WINDOW * 2)
    dnfs = last["status"].isin(DNF_STATUSES).sum()
    return round(float(1 - dnfs / len(last)), 3)