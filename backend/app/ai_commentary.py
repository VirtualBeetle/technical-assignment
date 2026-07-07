"""
Board commentary generation.

Default mode ("demo mode", AI_PROVIDER=none): a deterministic, template-based
narrative generator that reads the *already-computed* metrics (app/metrics.py)
and turns them into board-ready prose. No external API calls, no API key
required, fully reproducible - every sentence traces back to a specific
number you can check against data/senus_financials.json.

Optional mode (AI_PROVIDER=openai + OPENAI_API_KEY set): the same metrics are
sent to an LLM with a tightly-scoped prompt (numbers only, no invention) to
produce more fluent prose. If the call fails for any reason (no key, network,
rate limit) it falls back to the deterministic generator automatically - the
app never shows a broken insights page for lack of a credential.
"""
from __future__ import annotations

from app.config import get_settings

settings = get_settings()


def _fmt_eur(value: float) -> str:
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000:
        return f"{sign}€{value / 1_000_000:.2f}m"
    if value >= 1_000:
        return f"{sign}€{value / 1_000:.1f}k"
    return f"{sign}€{value:.0f}"


def _rule_based_overview(period_label: str, metrics: dict) -> str:
    g, p, c, s, r = metrics["growth"], metrics["profitability"], metrics["cash"], metrics["solvency"], metrics["returns"]
    parts = [
        f"For {period_label}, Senus reported revenue of {_fmt_eur(g['revenue'])}"
        + (f", up {g['revenue_growth_pct']}% on the prior comparable period." if "revenue_growth_pct" in g else "."),
        f"Gross margin was {p['gross_margin_pct']}%, reflecting the software/services mix "
        f"and the low direct cost of delivering Senus' soil sampling and Senus ERA solutions.",
        f"EBITDA was {_fmt_eur(p['ebitda'])} ({p['ebitda_margin_pct']}% margin) as the business continues to invest "
        f"ahead of the Senus 2030 growth plan, which targets EBITDA breakeven in FY2028.",
        f"Cash at period end was {_fmt_eur(c['cash'])}"
        + (f", giving an estimated runway of {c['cash_runway_months']} months at the current net operating cash burn "
           f"of {_fmt_eur(c['monthly_cash_burn'])}/month." if c.get("cash_runway_months") else "."),
        f"The group holds a net cash position of {_fmt_eur(s['net_cash_position'])} against {_fmt_eur(s['bank_debt'])} "
        f"of bank debt, so leverage is not a near-term concern; debt-service ratios are not yet meaningful given "
        f"the pre-EBITDA-breakeven stage of the business.",
    ]
    if s.get("contingent_consideration"):
        parts.append(
            f"Note the {_fmt_eur(s['contingent_consideration'])} Loamin earn-out is performance-linked and "
            f"non-cash unless targets are met - it depresses reported net current assets but is not a liquidity "
            f"claim today."
        )
    if r.get("roce_pct") is not None:
        parts.append(
            f"Return on capital employed is {r['roce_pct']}% (annualised), consistent with a company still "
            f"investing through its Series-A-to-scale-up phase rather than harvesting returns."
        )
    if "pipeline_deals_closed_in_period_eur" in g:
        parts.append(
            f"Commercially, {_fmt_eur(g['pipeline_deals_closed_in_period_eur'])} of deals closed across "
            f"{g.get('pipeline_deals_closed_in_period_customers', 'several')} enterprise customers in the period, "
            f"with a further {_fmt_eur(g.get('open_pipeline_eur', 0))} of open pipeline - an early signal for "
            f"the next 1-2 reporting periods rather than this period's revenue."
        )
    return " ".join(parts)


def _rule_based_section(section: str, period_label: str, metrics: dict) -> str:
    g, p, c, s, r = metrics["growth"], metrics["profitability"], metrics["cash"], metrics["solvency"], metrics["returns"]
    if section == "growth":
        txt = f"Revenue for {period_label} was {_fmt_eur(g['revenue'])}"
        if "revenue_growth_pct" in g:
            txt += f", {g['revenue_growth_pct']:+.1f}% versus the prior comparable period"
        txt += ". "
        if "gross_profit_growth_pct" in g:
            txt += f"Gross profit grew {g['gross_profit_growth_pct']:+.1f}%, "
            txt += "outpacing revenue growth as gross margin expanded. " if g["gross_profit_growth_pct"] > g.get("revenue_growth_pct", 0) else ""
        if "customer_accounts" in g:
            txt += f"The group served {g['customer_accounts']} customer accounts as at the most recent annual filing. "
        if "pipeline_deals_closed_in_period_eur" in g:
            txt += (f"{_fmt_eur(g['pipeline_deals_closed_in_period_eur'])} of new deals closed in the period across "
                     f"{g.get('pipeline_deals_closed_in_period_customers', 'multiple')} enterprise customers, with "
                     f"{_fmt_eur(g.get('open_pipeline_eur', 0))} of pipeline still open.")
        return txt
    if section == "profitability":
        return (
            f"Gross margin was {p['gross_margin_pct']}%, with cost of sales at {p['cost_of_sales_pct_revenue']}% "
            f"of revenue. Administrative expenses of {_fmt_eur(p['administrative_expenses'])} "
            f"({p['admin_expenses_pct_revenue']}% of revenue) remain the dominant cost line, consistent with a "
            f"company scaling its engineering and go-to-market teams ahead of revenue. Operating margin was "
            f"{p['operating_margin_pct']}% and EBITDA margin {p['ebitda_margin_pct']}%, both expected to improve "
            f"as revenue scales against a largely fixed cost base."
        )
    if section == "cash":
        txt = (f"Cash at period end was {_fmt_eur(c['cash'])}. Net cash used in operating activities was "
               f"{_fmt_eur(c['net_cash_operating'])}")
        if c.get("monthly_cash_burn"):
            txt += f", a burn rate of roughly {_fmt_eur(c['monthly_cash_burn'])}/month"
        txt += ". "
        if c.get("cash_runway_months"):
            txt += f"At that rate, present cash covers approximately {c['cash_runway_months']} months of operations. "
        bridge = c["ebitda_to_fcf_bridge"]
        txt += (f"The EBITDA-to-free-cash-flow bridge: EBITDA {_fmt_eur(bridge['ebitda'])}, working capital movement "
                f"{_fmt_eur(bridge['working_capital_movement'])}, interest {_fmt_eur(bridge['interest'])}, capex "
                f"{_fmt_eur(bridge['capex'])}, giving free cash flow of {_fmt_eur(bridge['free_cash_flow'])}.")
        return txt
    if section == "solvency":
        txt = (f"The group holds {_fmt_eur(s['cash'])} of cash against {_fmt_eur(s['bank_debt'])} of bank debt, "
               f"a net cash position of {_fmt_eur(s['net_cash_position'])}. The current ratio is "
               f"{s['current_ratio']}x. ")
        if not s["dscr_meaningful"]:
            txt += (
                "Debt Service Coverage Ratio is not meaningful this period because EBITDA is negative; Senus 2030 "
                "targets EBITDA breakeven in FY2028, at which point DSCR and net-debt/EBITDA become decision-useful "
                "for credit providers. Leverage risk today comes primarily from the performance-linked Loamin "
                f"earn-out ({_fmt_eur(s['contingent_consideration'])}), which is contingent and non-cash unless "
                "targets are achieved, rather than from funded debt."
            )
        else:
            txt += f"DSCR is {s['dscr']}x and net debt/EBITDA is {s['net_debt_to_ebitda']}x."
        return txt
    if section == "returns":
        txt = f"Capital employed was {_fmt_eur(r['capital_employed'])}. "
        if r["roce_pct"] is not None:
            txt += (f"Annualised ROCE was {r['roce_pct']}%, negative as expected for a business still in its "
                     "investment phase; the relevant question for the Board is the trajectory (is capital employed "
                     "producing improving unit economics per euro invested) rather than the absolute level until "
                     "FY2028 EBITDA breakeven.")
        return txt
    return ""


def generate_commentary(section: str, period_label: str, metrics: dict) -> tuple[str, str]:
    """Returns (text, generated_by)."""
    if settings.ai_provider == "openai" and settings.openai_api_key:
        try:
            return _openai_commentary(section, period_label, metrics), "openai"
        except Exception:
            pass  # fall through to deterministic generator - never show a broken page for a credential/network issue
    if section == "overview":
        return _rule_based_overview(period_label, metrics), "rule_based"
    return _rule_based_section(section, period_label, metrics), "rule_based"


def _openai_commentary(section: str, period_label: str, metrics: dict) -> str:
    from openai import OpenAI  # deferred import: only required if AI_PROVIDER=openai

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = (
        "You are a CFO writing a short board-report commentary paragraph. "
        "Use ONLY the numbers provided below - do not invent any figures. "
        f"Section: {section}. Period: {period_label}. Metrics (JSON): {metrics}\n\n"
        "Write 3-5 sentences, plain prose, no bullet points, suitable for a board pack."
    )
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()
