"""
Metrics engine: pure functions that turn raw extracted line items into the
board-report ratios called for in the assignment brief (Growth & Revenue,
Profitability, Cash & Liquidity, Solvency & Leverage, Returns).

Kept deliberately framework-free (plain dicts in, plain dicts out) so it can
be unit tested in isolation (see backend/tests/test_metrics.py) without a
database or web framework in the loop.

Sign convention (see app/ingestion/extract_pdfs.py normalize_signs for how
this is enforced during extraction too):
  - revenue, gross_profit, cash, debtors, assets: positive
  - cost_of_sales, administrative_expenses, distribution_costs: positive
    magnitudes (i.e. NOT already negated)
  - operating_loss, loss_before_tax, loss_for_period: negative (a loss)
"""
from __future__ import annotations

MONTHS_IN_PERIOD = {"annual": 12, "half_year": 6}


def _months(period: dict) -> int:
    return MONTHS_IN_PERIOD.get(period["period_type"], 12)


def _income(period: dict, key: str, default: float = 0.0) -> float:
    return period.get("income_statement", {}).get(key, default)


def _balance(period: dict, key: str, default: float = 0.0) -> float:
    return period.get("balance_sheet", {}).get(key, default)


def _cashflow(period: dict, key: str, default: float = 0.0) -> float:
    return period.get("cash_flow", {}).get(key, default)


def ebitda(period: dict) -> float:
    """EBITDA = operating loss/profit + depreciation (no amortisation of
    intangibles has been charged yet in these filings, so D&A == depreciation
    here; the field is still called 'ebitda' rather than 'ebit_plus_dep' so
    the frontend/README naming matches standard board-report terminology)."""
    return _income(period, "operating_loss") + _income(period, "depreciation")


def growth_metrics(current: dict, prior: dict | None) -> dict:
    revenue = _income(current, "revenue")
    metrics = {
        "revenue": revenue,
        "gross_profit": _income(current, "gross_profit"),
    }
    if prior:
        prior_revenue = _income(prior, "revenue")
        if prior_revenue:
            metrics["revenue_growth_pct"] = round(100 * (revenue - prior_revenue) / prior_revenue, 1)
        prior_gp = _income(prior, "gross_profit")
        if prior_gp:
            metrics["gross_profit_growth_pct"] = round(
                100 * (_income(current, "gross_profit") - prior_gp) / prior_gp, 1
            )
    commercial = current.get("commercial", {})
    if "customer_accounts" in commercial:
        metrics["customer_accounts"] = commercial["customer_accounts"]
    for key in (
        "pipeline_deals_closed_in_period_eur",
        "pipeline_deals_closed_in_period_customers",
        "open_pipeline_eur",
        "deals_closed_final_2_months_2025_eur",
        "deals_closed_final_2_months_2025_count",
    ):
        if key in commercial:
            metrics[key] = commercial[key]
    return metrics


def profitability_metrics(current: dict) -> dict:
    revenue = _income(current, "revenue") or 1e-9
    gross_profit = _income(current, "gross_profit")
    operating_loss = _income(current, "operating_loss")
    eb = ebitda(current)
    return {
        "gross_margin_pct": round(100 * gross_profit / revenue, 1),
        "operating_margin_pct": round(100 * operating_loss / revenue, 1),
        "ebitda": eb,
        "ebitda_margin_pct": round(100 * eb / revenue, 1),
        "cost_of_sales_pct_revenue": round(100 * _income(current, "cost_of_sales") / revenue, 1),
        "admin_expenses_pct_revenue": round(100 * _income(current, "administrative_expenses") / revenue, 1),
        "administrative_expenses": _income(current, "administrative_expenses"),
        "cost_of_sales": _income(current, "cost_of_sales"),
    }


def cash_metrics(current: dict) -> dict:
    cash = _balance(current, "cash")
    net_cash_operating = _cashflow(current, "net_cash_operating")
    months = _months(current)
    monthly_burn = -net_cash_operating / months if months else None

    eb = ebitda(current)
    working_capital_movement = _cashflow(current, "working_capital_movement", 0.0)
    interest = _income(current, "interest_payable")
    capex = _cashflow(current, "capex", 0.0)
    free_cash_flow = eb + working_capital_movement - interest - capex

    result = {
        "cash": cash,
        "net_cash_operating": net_cash_operating,
        "monthly_cash_burn": round(monthly_burn, 0) if monthly_burn else None,
        "cash_runway_months": round(cash / monthly_burn, 1) if monthly_burn and monthly_burn > 0 else None,
        "ebitda_to_fcf_bridge": {
            "ebitda": round(eb, 0),
            "working_capital_movement": round(working_capital_movement, 0),
            "interest": round(-interest, 0),
            "capex": round(-capex, 0),
            "free_cash_flow": round(free_cash_flow, 0),
        },
        "working_capital": _balance(current, "current_assets", 0.0) - _balance(current, "creditors_due_within_1yr", 0.0),
    }
    debtors = _balance(current, "debtors")
    revenue = _income(current, "revenue")
    if revenue:
        result["debtor_days"] = round(debtors / revenue * (365 * _months(current) / 12), 0)
    return result


def solvency_metrics(current: dict) -> dict:
    cash = _balance(current, "cash")
    debt_after_1yr = _balance(current, "creditors_due_after_1yr")
    bank_debt_total = current.get("debt", {}).get("bank_debt_total_eur", debt_after_1yr)
    net_cash_position = cash - bank_debt_total

    eb = ebitda(current)
    interest = _income(current, "interest_payable")
    current_assets = _balance(current, "current_assets")
    current_liabilities = _balance(current, "creditors_due_within_1yr")

    result = {
        "cash": cash,
        "bank_debt": bank_debt_total,
        "net_cash_position": net_cash_position,
        "current_ratio": round(current_assets / current_liabilities, 2) if current_liabilities else None,
        "interest_cover_x": round(abs(eb) / interest, 1) if interest else None,
        "contingent_consideration": _balance(current, "contingent_consideration", 0.0),
    }
    # DSCR / net-debt-to-EBITDA are only meaningful once EBITDA is positive;
    # Senus 2030 targets EBITDA-positive in FY2028, so we report but flag them.
    result["dscr_meaningful"] = eb > 0
    if eb > 0:
        annual_debt_service = interest + bank_debt_total / 5  # straight-line proxy, no amortisation schedule disclosed
        result["dscr"] = round(eb / annual_debt_service, 2) if annual_debt_service else None
        result["net_debt_to_ebitda"] = round(-net_cash_position / eb, 2)
    else:
        result["dscr"] = None
        result["net_debt_to_ebitda"] = None
    return result


def returns_metrics(current: dict) -> dict:
    total_assets_less_current_liabilities = current.get("balance_sheet", {}).get(
        "total_assets_less_current_liabilities"
    )
    if total_assets_less_current_liabilities is None:
        # Derive it where the filing doesn't disclose the subtotal directly.
        total_assets_less_current_liabilities = _balance(current, "net_current_assets") + max(
            _balance(current, "tangible_assets") + _balance(current, "goodwill") + _balance(current, "development_costs"),
            0,
        )
    capital_employed = total_assets_less_current_liabilities
    operating_loss = _income(current, "operating_loss")
    months = _months(current)
    annualisation_factor = 12 / months if months else 1

    roce_pct = None
    if capital_employed:
        roce_pct = round(100 * (operating_loss * annualisation_factor) / capital_employed, 1)

    return {
        "capital_employed": capital_employed,
        "operating_result_annualised": round(operating_loss * annualisation_factor, 0),
        "roce_pct": roce_pct,
        "net_assets": _balance(current, "net_assets"),
    }


def compute_all_metrics(current: dict, prior: dict | None = None) -> dict:
    return {
        "growth": growth_metrics(current, prior),
        "profitability": profitability_metrics(current),
        "cash": cash_metrics(current),
        "solvency": solvency_metrics(current),
        "returns": returns_metrics(current),
    }
