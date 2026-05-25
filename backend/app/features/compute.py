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
 