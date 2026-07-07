from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Commentary, FinancialPeriod, User
from app.schemas import CommentaryOut
from app.security import get_current_user

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("", response_model=list[CommentaryOut])
def get_insights(
    period: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    p = db.query(FinancialPeriod).filter(FinancialPeriod.period_key == period).first()
    if not p:
        raise HTTPException(status_code=404, detail="Period not found")
    return db.query(Commentary).filter(Commentary.period_id == p.id).all()
