from fastapi import APIRouter
from app.api.v1 import predictions, standings, races, health

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(predictions.router)
api_router.include_router(standings.router)
api_router.include_router(races.router)
api_router.include_router(health.router)