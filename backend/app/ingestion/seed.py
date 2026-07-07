"""
Seeds the database from the curated gold dataset (data/senus_financials.json).

Run with:  python -c "from app.ingestion.seed import main; main()"
(also called automatically on API startup if the DB is empty - see app/main.py)
"""
from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.ingestion.gold_dataset import load_gold_dataset
from app.metrics import compute_all_metrics
from app.ai_commentary import generate_commentary
from app.models import (
    Commentary,
    CommercialFact,
    Company,
    Director,
    FinancialPeriod,
    LineItem,
    MetricSnapshot,
)
from app.security import ensure_demo_user


def _to_snapshot_value(value):
    """Coerce a metrics-engine output value to a plain float for storage in
    MetricSnapshot.value (a Float column). bool is a subclass of int in
    Python, so an isinstance(x, (int, float)) check alone treats e.g.
    dscr_meaningful (True/False) as numeric - SQLite silently accepts that
    (its columns are dynamically typed), but Postgres's stricter typing
    rejects a Python bool going into a double precision column. Converting
    explicitly here keeps the information (0.0/1.0) instead of just dropping
    it, since the frontend reads dscr_meaningful back out of this table.
    """
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _flatten_facts(d, prefix=""):
    """Flatten nested dicts/lists of primitives into {key: value} for storage
    as CommercialFact rows (numeric or text)."""
    flat = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, bool):
            flat[key] = 1.0 if v else 0.0
        elif isinstance(v, (int, float)):
            flat[key] = v
        elif isinstance(v, str):
            flat[key] = v
        elif isinstance(v, list):
            flat[key] = "; ".join(str(x) for x in v)
    return flat


def seed(db: Session) -> None:
    gold = load_gold_dataset()

    if db.query(Company).first():
        print("Database already seeded - skipping.")
        return

    comp = gold["company"]
    company = Company(
        name=comp["name"],
        company_number=comp.get("company_number"),
        sector=comp.get("sector"),
        founded_year=comp.get("incorporated"),
        hq=comp.get("registered_office"),
        auditor=comp.get("auditor"),
        ticker=comp["listing"]["ticker"],
        isin=comp["listing"]["isin"],
        listing_market=comp["listing"]["market"],
        admission_date=date.fromisoformat(comp["listing"]["admission_date"]),
        admission_price=comp["listing"]["admission_share_price_eur"],
        market_cap_at_admission=comp["listing"]["market_cap_at_admission_eur"],
        issued_share_capital=comp["listing"]["issued_share_capital"],
        strategy_name=comp["strategy"]["name"],
        strategy_target_cagr_pct=comp["strategy"]["target_revenue_cagr_pct"],
        ebitda_positive_target_fy=comp["strategy"]["ebitda_positive_target_fy"],
    )
    db.add(company)
    db.flush()

    for d in comp["directors"]:
        db.add(Director(company_id=company.id, name=d["name"], role=d["role"]))

    period_rows = {}
    for p in gold["periods"]:
        row = FinancialPeriod(
            company_id=company.id,
            period_key=p["id"],
            label=p["label"],
            period_type=p["period_type"],
            start_date=date.fromisoformat(p["start_date"]),
            end_date=date.fromisoformat(p["end_date"]),
            consolidation=p.get("consolidation", "group"),
            audited=p.get("audited", False),
            source_document=p.get("source_document"),
        )
        db.add(row)
        db.flush()
        period_rows[p["id"]] = row

        for statement in ("income_statement", "balance_sheet", "cash_flow"):
            for key, value in p.get(statement, {}).items():
                numeric = _to_snapshot_value(value)
                if numeric is not None:
                    db.add(LineItem(period_id=row.id, statement=statement, key=key, value=numeric))

        for key, value in _flatten_facts(p.get("commercial", {})).items():
            if isinstance(value, (int, float)):
                db.add(CommercialFact(period_id=row.id, key=key, value_numeric=value))
            else:
                db.add(CommercialFact(period_id=row.id, key=key, value_text=str(value)))

    db.flush()

    ordered_period_ids = ["FY2024", "FY2025", "HY_DEC_2024", "HY_DEC_2025"]
    prior_map = {"FY2025": "FY2024", "HY_DEC_2025": "HY_DEC_2024"}

    periods_by_id = {p["id"]: p for p in gold["periods"]}
    for pid in ordered_period_ids:
        period = periods_by_id[pid]
        prior = periods_by_id.get(prior_map.get(pid))
        metrics = compute_all_metrics(period, prior)
        row = period_rows[pid]

        for category, cat_metrics in metrics.items():
            for key, value in cat_metrics.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        numeric = _to_snapshot_value(sub_value)
                        if numeric is not None:
                            db.add(MetricSnapshot(period_id=row.id, category=category, key=f"{key}.{sub_key}", value=numeric))
                else:
                    numeric = _to_snapshot_value(value)
                    if numeric is not None:
                        db.add(MetricSnapshot(period_id=row.id, category=category, key=key, value=numeric))

        for section in ("overview", "growth", "profitability", "cash", "solvency", "returns"):
            text, generated_by = generate_commentary(section, period["label"], metrics)
            db.add(Commentary(period_id=row.id, section=section, text=text, generated_by=generated_by))

    db.commit()
    ensure_demo_user(db)
    print(f"Seeded {len(period_rows)} periods for {company.name}.")


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
