from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Company, Director, FinancialPeriod, User
from app.schemas import CompanyOut, DirectorOut, PeriodOut
from app.security import get_current_user

router = APIRouter(prefix="/api/company", tags=["company"])


@router.get("", response_model=CompanyOut)
def get_company(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Company).first()


@router.get("/directors", response_model=list[DirectorOut])
def get_directors(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Director).all()


@router.get("/periods", response_model=list[PeriodOut])
def get_periods(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(FinancialPeriod).order_by(FinancialPeriod.start_date).all()
