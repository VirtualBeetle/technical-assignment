from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    company_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sector: Mapped[str | None] = mapped_column(Text, nullable=True)
    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hq: Mapped[str | None] = mapped_column(String(255), nullable=True)
    auditor: Mapped[str | None] = mapped_column(String(255), nullable=True)

    ticker: Mapped[str | None] = mapped_column(String(20), nullable=True)
    isin: Mapped[str | None] = mapped_column(String(20), nullable=True)
    listing_market: Mapped[str | None] = mapped_column(String(255), nullable=True)
    admission_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    admission_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    market_cap_at_admission: Mapped[float | None] = mapped_column(Float, nullable=True)
    issued_share_capital: Mapped[int | None] = mapped_column(Integer, nullable=True)
    strategy_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    strategy_target_cagr_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    ebitda_positive_target_fy: Mapped[str | None] = mapped_column(String(50), nullable=True)

    directors: Mapped[list["Director"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    periods: Mapped[list["FinancialPeriod"]] = relationship(back_populates="company", cascade="all, delete-orphan")


class Director(Base):
    __tablename__ = "directors"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(255))

    company: Mapped[Company] = relationship(back_populates="directors")


class FinancialPeriod(Base):
    __tablename__ = "financial_periods"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    period_key: Mapped[str] = mapped_column(String(50), unique=True)  # e.g. "FY2024", "HY_DEC_2025"
    label: Mapped[str] = mapped_column(String(255))
    period_type: Mapped[str] = mapped_column(String(20))  # "annual" | "half_year"
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    consolidation: Mapped[str] = mapped_column(String(20), default="group")
    audited: Mapped[bool] = mapped_column(Boolean, default=False)
    source_document: Mapped[str | None] = mapped_column(String(255), nullable=True)

    company: Mapped[Company] = relationship(back_populates="periods")
    line_items: Mapped[list["LineItem"]] = relationship(back_populates="period", cascade="all, delete-orphan")
    commercial_facts: Mapped[list["CommercialFact"]] = relationship(back_populates="period", cascade="all, delete-orphan")
    metrics: Mapped[list["MetricSnapshot"]] = relationship(back_populates="period", cascade="all, delete-orphan")
    commentary: Mapped[list["Commentary"]] = relationship(back_populates="period", cascade="all, delete-orphan")


class LineItem(Base):
    """Generic (statement, key) -> numeric value store.

    Kept as an EAV-style table (rather than one column per line item) so new
    financial statement line items can be extracted and stored without a schema
    migration - important given source filings evolve (e.g. Loamin's goodwill /
    contingent consideration only appear from HY_DEC_2025 onwards).
    """

    __tablename__ = "line_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("financial_periods.id"))
    statement: Mapped[str] = mapped_column(String(30))  # income_statement | balance_sheet | cash_flow | headcount | debt
    key: Mapped[str] = mapped_column(String(100))
    value: Mapped[float] = mapped_column(Float)

    period: Mapped[FinancialPeriod] = relationship(back_populates="line_items")


class CommercialFact(Base):
    """Non-financial-statement facts: pipeline, bookings, contracts, headcount notes."""

    __tablename__ = "commercial_facts"

    id: Mapped[int] = mapped_column(primary_key=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("financial_periods.id"))
    key: Mapped[str] = mapped_column(String(100))
    value_numeric: Mapped[float | None] = mapped_column(Float, nullable=True)
    value_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    period: Mapped[FinancialPeriod] = relationship(back_populates="commercial_facts")


class MetricSnapshot(Base):
    """Cached output of the metrics engine (app/metrics.py) for a given period."""

    __tablename__ = "metric_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("financial_periods.id"))
    category: Mapped[str] = mapped_column(String(30))  # growth | profitability | cash | solvency | returns
    key: Mapped[str] = mapped_column(String(100))
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(20), default="eur")  # eur | pct | months | ratio | days
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    period: Mapped[FinancialPeriod] = relationship(back_populates="metrics")


class Commentary(Base):
    """AI-generated (or rule-based fallback) board commentary per section/period."""

    __tablename__ = "commentary"

    id: Mapped[int] = mapped_column(primary_key=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("financial_periods.id"))
    section: Mapped[str] = mapped_column(String(30))  # growth | profitability | cash | solvency | returns | overview
    text: Mapped[str] = mapped_column(Text)
    generated_by: Mapped[str] = mapped_column(String(20), default="rule_based")  # rule_based | openai
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    period: Mapped[FinancialPeriod] = relationship(back_populates="commentary")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="ceo")
