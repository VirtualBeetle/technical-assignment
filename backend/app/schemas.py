from datetime import date

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: str
    password: str


class CompanyOut(BaseModel):
    id: int
    name: str
    company_number: str | None
    sector: str | None
    founded_year: int | None
    hq: str | None
    auditor: str | None
    ticker: str | None
    isin: str | None
    listing_market: str | None
    admission_date: date | None
    admission_price: float | None
    market_cap_at_admission: float | None
    issued_share_capital: int | None
    strategy_name: str | None
    strategy_target_cagr_pct: float | None
    ebitda_positive_target_fy: str | None

    class Config:
        from_attributes = True


class DirectorOut(BaseModel):
    name: str
    role: str

    class Config:
        from_attributes = True


class PeriodOut(BaseModel):
    period_key: str
    label: str
    period_type: str
    start_date: date
    end_date: date
    consolidation: str
    audited: bool
    source_document: str | None

    class Config:
        from_attributes = True


class MetricsResponse(BaseModel):
    period: PeriodOut
    metrics: dict


class CommentaryOut(BaseModel):
    section: str
    text: str
    generated_by: str

    class Config:
        from_attributes = True
