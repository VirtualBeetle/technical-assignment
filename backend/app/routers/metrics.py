from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FinancialPeriod, MetricSnapshot, User
from app.security import get_current_user

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

VALID_CATEGORIES = {"growth", "profitability", "cash", "solvency", "returns"}


def _unflatten(rows: list[MetricSnapshot]) -> dict:
    result: dict = {}
    for row in rows:
        if "." in row.key:
            parent, child = row.key.split(".", 1)
            result.setdefault(parent, {})[child] = row.value
        else:
            result[row.key] = row.value
    return result


@router.get("/{category}")
def get_metrics(
    category: str,
    period: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if category not in VALID_CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Unknown category '{category}'")

    query = db.query(FinancialPeriod).order_by(FinancialPeriod.start_date)
    periods = [query.filter(FinancialPeriod.period_key == period).first()] if period else query.all()
    periods = [p for p in periods if p is not None]
    if not periods:
        raise HTTPException(status_code=404, detail="Period not found")

    results = []
    for p in periods:
        rows = (
            db.query(MetricSnapshot)
            .filter(MetricSnapshot.period_id == p.id, MetricSnapshot.category == category)
            .all()
        )
        results.append(
            {
                "period": {
                    "period_key": p.period_key,
                    "label": p.label,
                    "period_type": p.period_type,
                    "start_date": str(p.start_date),
                    "end_date": str(p.end_date),
                },
                "metrics": _unflatten(rows),
            }
        )
    return results if period is None else results[0]
