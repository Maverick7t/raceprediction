"""
GET /api/v1/races   → all race keys in qualifying_raw, newest first
"""

from fastapi import APIRouter
from sqlalchemy import text
from app.db.session import get_session
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/races", tags=["races"])


@router.get("")
def list_races():
    """All race keys present in qualifying_raw, newest first."""
    with get_session() as session:
        result = session.execute(text("""
            SELECT DISTINCT race_key, year, round, race_name, circuit_id
            FROM qualifying_raw
            ORDER BY year DESC, round DESC
        """))
        rows = [dict(r) for r in result.mappings().all()]
    return {"count": len(rows), "races": rows}