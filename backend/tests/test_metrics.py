"""
Unit tests for the metrics engine, using the same gold dataset the live app
runs on. These numbers were independently hand-verified against the source
PDFs (see data/senus_financials.json "_meta" and "provenance") - this test
suite is what "how did you validate the outputs" means in practice.
"""
import json
from pathlib import Path

import pytest

from app.metrics import compute_all_metrics, ebitda

GOLD_PATH = Path(__file__).resolve().parents[2] / "data" / "senus_financials.json"


@pytest.fixture(scope="module")
def periods():
    with open(GOLD_PATH) as f:
        gold = json.load(f)
    return {p["id"]: p for p in gold["periods"]}


def test_hy26_revenue_growth(periods):
    m = compute_all_metrics(periods["HY_DEC_2025"], periods["HY_DEC_2024"])
    assert m["growth"]["revenue"] == 354813
    assert m["growth"]["revenue_growth_pct"] == pytest.approx(4.1, abs=0.05)


def test_hy26_gross_margin(periods):
    m = compute_all_metrics(periods["HY_DEC_2025"], periods["HY_DEC_2024"])
    assert m["profitability"]["gross_margin_pct"] == pytest.approx(81.7, abs=0.05)


def test_fy25_vs_fy24_revenue_growth(periods):
    m = compute_all_metrics(periods["FY2025"], periods["FY2024"])
    # 836,991 vs 688,317 -> +21.6%
    assert m["growth"]["revenue_growth_pct"] == pytest.approx(21.6, abs=0.05)


def test_ebitda_matches_half_year_cashflow_subtotal(periods):
    # The HY26 cash-flow statement's pre-working-capital subtotal (-473,739)
    # is, by construction, loss + interest + depreciation = EBITDA. This is
    # an internal-consistency check across two different statements in the
    # SAME source filing, not just a re-statement of our own formula.
    assert ebitda(periods["HY_DEC_2025"]) == pytest.approx(-473739, abs=1)
    assert ebitda(periods["HY_DEC_2024"]) == pytest.approx(-395561, abs=1)


def test_net_cash_position_hy26(periods):
    m = compute_all_metrics(periods["HY_DEC_2025"], periods["HY_DEC_2024"])
    # 735,189 cash vs 76,500 bank debt -> net cash, not net debt
    assert m["solvency"]["net_cash_position"] == pytest.approx(658689, abs=1)
    assert m["solvency"]["dscr_meaningful"] is False


def test_cash_runway_hy26(periods):
    m = compute_all_metrics(periods["HY_DEC_2025"], periods["HY_DEC_2024"])
    assert m["cash"]["cash_runway_months"] == pytest.approx(10.8, abs=0.1)
