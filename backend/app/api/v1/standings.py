"""
GET /api/v1/standings/drivers?year=2024
GET /api/v1/standings/constructors?year=2024
"""

from fastapi import APIRouter, HTTPException, Query
from app.db.repositories.standings_repo import StandingsRepository
from app.core.logging import get_logger
from datetime import datetime

logger = get_logger(__name__)
router = APIRouter(prefix="/standings", tags=["standings"])

_repo = StandingsRepository()


@router.get("/drivers")
def get_driver_standings(year: int = Query(default=None)):
    resolved_year = year or (_repo.latest_year() or datetime.now().year)
    df = _repo.get_driver_standings(resolved_year)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No driver standings for year={resolved_year}")
    return {"year": resolved_year, "standings": df.to_dict(orient="records")}


@router.get("/constructors")
def get_constructor_standings(year: int = Query(default=None)):
    resolved_year = year or (_repo.latest_year() or datetime.now().year)
    df = _repo.get_constructor_standings(resolved_year)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No constructor standings for year={resolved_year}")
    return {"year": resolved_year, "standings": df.to_dict(orient="records")}