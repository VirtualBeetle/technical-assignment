# Senus PLC — AI-Native Board Report Platform

Built for the Assiduous Corp Technology Graduate assignment: an AI-native Board Report
platform for Senus PLC, for Management, the Board, Equity Investors and Credit Providers.

**Live demo:** _add Render frontend URL_
**Demo login:** `ceo@senus.com` / `Senus2030!`
**GitHub:** [github.com/VirtualBeetle/senus-board-report](https://github.com/VirtualBeetle/senus-board-report)

## What this is

- **Backend** — FastAPI + SQLAlchemy + PostgreSQL/SQLite REST API over structured financial
  data extracted from Senus PLC's real regulatory filings.
- **Extraction pipeline** — OCR + regex turns raw source PDFs (native-text and scanned) into
  structured line items, validated against a hand-verified dataset.
- **Metrics engine** — growth, margins, EBITDA, cash runway, EBITDA→FCF bridge,
  solvency/leverage, ROCE.
- **AI commentary layer** — rule-based board-ready prose by default, optional LLM upgrade
  with an API key.
- **Frontend** — Next.js + TypeScript + Tailwind + Recharts dashboard: Overview, Growth &
  Revenue, Profitability, Cash & Liquidity, Solvency & Leverage, Returns, AI Insights.
  Periods: FY2024, FY2025, H1 FY2025, H1 FY2026.

## Architecture

```
                      ┌───────────────────────────┐
  Senus source PDFs   │  data/source_documents/*  │
  (6 filings, some     └────────────┬──────────────┘
   native text, some                │
   scanned images)                  ▼
                      ┌───────────────────────────────────┐
                      │  backend/app/ingestion             │
                      │   extract_pdfs.py  (OCR + regex,   │
                      │     validated against gold data)   │
                      │   gold_dataset.py  (curated JSON,  │
                      │     source of truth for the app)   │
                      │   seed.py  (loads DB + computes    │
                      │     metrics + AI commentary)       │
                      └────────────┬────────────────────────┘
                                   ▼
                      ┌───────────────────────────┐
                      │  PostgreSQL / SQLite        │
                      │   companies, periods,       │
                      │   line_items, metrics,       │
                      │   commentary, users          │
                      └────────────┬────────────────┘
                                   ▼
                      ┌───────────────────────────┐        ┌─────────────────────────┐
                      │  FastAPI backend           │◄──────►│  app/metrics.py          │
                      │   /api/auth  /api/company   │        │  app/ai_commentary.py   │
                      │   /api/metrics/{category}   │        └─────────────────────────┘
                      │   /api/insights              │
                      └────────────┬────────────────┘
                                   │ REST + JWT
                                   ▼
                      ┌───────────────────────────┐
                      │  Next.js frontend            │
                      │   Login → Dashboard          │
                      │   Growth / Profitability /   │
                      │   Cash / Solvency / Returns / │
                      │   AI Insights                 │
                      └───────────────────────────┘
```

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python / FastAPI | Matches the JD's core stack; async-ready, typed, auto-docs at `/docs`. |
| Database | PostgreSQL (prod) / SQLite (local dev) | Same SQLAlchemy models, `DATABASE_URL` switches engines. |
| ORM | SQLAlchemy 2.0 | Typed models, explicit schema, no framework lock-in. |
| PDF/OCR | pdfplumber, pytesseract, pdf2image | Two of six filings are scanned images with no text layer — needed real OCR. |
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind + Recharts | Matches the JD's stack; client-rendered SPA fits an authenticated dashboard. |
| Auth | JWT (python-jose) + bcrypt (passlib) | Deliberately minimal — see Assumptions. |
| AI | Rule-based generator by default; optional OpenAI-compatible LLM call | Same pattern as my FAIR_GPT project: works with zero credentials, upgrades cleanly with a key. |
| Deployment | Docker Compose (local) / Render Blueprint (`render.yaml`, cloud) | Same containers run locally and in production. |

## AI-assisted development workflow

This project was built in an AI-assisted session (Claude), reviewed and validated at every step:

- **Research** — read the brief, JD, and all six Senus source filings before writing any code.
- **Manual figure verification** — every number in `data/senus_financials.json` read directly
  off the source PDFs and cited to its source in the `provenance` section.
- **AI-assisted extraction pipeline** — `extract_pdfs.py` iterated against the actual PDFs
  until it reproduced the gold dataset (see Validation below).
- **Iterative build** — schema, metrics engine, API, frontend built and tested layer by layer.
- **AI commentary** — deterministic fallback by default; the LLM path is a genuine drop-in
  upgrade, not vaporware.

## AI extraction pipeline

```bash
cd backend
pip install -r requirements.txt
python -c "from app.ingestion.extract_pdfs import run; run()"
```

- OCR fallback (Tesseract via `pdf2image`) for the two filings with no embedded text layer.
- Regex tuned to how Irish FRS 102 small-company accounts lay out two-column statements.
- `normalize_signs` reconciles differing sign conventions between the annual and half-year filings.
- `validate_against_gold` diffs every extracted value against the hand-verified dataset.

**Validation:** 57/57 (100%) of targeted fields matched. First pass was 47/57 (82.5%); all 10
mismatches traced to the sign-convention issues above, fixed in `normalize_signs`. The live app
seeds from the human-reviewed `data/senus_financials.json`, not raw pipeline output — the
extraction pipeline is real and validated, but a review step sits between AI output and the
board report, same as a real fintech would do. `backend/tests/test_metrics.py` unit-tests the
metrics engine against hand-calculated figures.

## Data model

- `companies`, `directors` — Senus PLC profile, listing details, Senus 2030 strategy targets.
- `financial_periods` — FY2024, FY2025 (annual, audited), H1 FY2025, H1 FY2026 (half-year, unaudited).
- `line_items` — EAV-style `(statement, key) → value` per period, so new line items (e.g.
  Loamin goodwill from H1 FY2026) don't require a schema migration.
- `commercial_facts` — non-statement facts: pipeline value, deals closed, named contracts.
- `metric_snapshots` — cached metrics-engine output per period/category.
- `commentary` — AI-generated (or rule-based) board commentary per period/section.
- `users` — single demo CEO account.

## Running it

- **Live demo** — _add Render frontend URL_, no setup needed.
- **Docker Compose** — `docker compose up --build` → frontend `localhost:3000`, backend `localhost:8000/docs`.
- **Local dev, no Docker** — `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`,
  then in another terminal `cd frontend && npm install && npm run dev`.
- **Extraction validation report** — `cd backend && python -c "from app.ingestion.extract_pdfs import run; run()"`
- **Tests** — `cd backend && python -m pytest tests/ -v`

## Deploying to Render

- Push to GitHub, then in the [Render dashboard](https://dashboard.render.com) click
  **New → Blueprint** and point it at the repo.
- Render reads `render.yaml` and provisions one click: Postgres + backend + frontend.
- Root-context Docker build bakes `data/` into the backend image; no manual env vars needed
  (`JWT_SECRET` auto-generated, `DATABASE_URL` wired automatically).
- The frontend's Next.js rewrite proxies `/api/*` to the backend over Render's private
  network, so there's no CORS configuration to get right.
- Free tier: services cold-start after 15 min idle (~30-60s to wake), Postgres expires after
  90 days. Bump `plan:` to `starter` in `render.yaml` for a longer review window.
- For real LLM commentary instead of the demo-mode generator, set `AI_PROVIDER=openai` and
  `OPENAI_API_KEY` as env vars on the backend service after deploy.

## Assumptions

- **Auth is demo-grade** — single hardcoded CEO account, JWT in `localStorage`. A real
  deployment would add refresh tokens, httpOnly cookies, and proper RBAC.
- **The Senus Limited balance sheet as at 8 Dec 2025 is company-only (parent), not
  consolidated** — prepared for the CRO re-registration, pre-dates the Loamin acquisition at
  group level. Used only as a standalone credit/liquidity cross-check.
- **EBITDA = operating loss + depreciation** — no intangible amortisation charged yet, so
  EBITDA and "EBIT + depreciation" are the same number here.
- **DSCR and Net Debt/EBITDA reported as "not yet meaningful"** while EBITDA is negative,
  rather than shown as a nonsensical negative ratio — Senus 2030 targets EBITDA breakeven in FY2028.
- **Customer-account count (138) is a single data point**, not a time series — shown as a KPI;
  pipeline figures from H1 FY2026 are shown as forward-looking context, not restated as revenue.
- **AI commentary defaults to rule-based**, not because the LLM path isn't real, but so the
  app is always demoable without an API key; it falls back automatically if the LLM call fails.

## What I'd do next with more time

- Wire the LLM structuring stage into `extract_pdfs.py` itself (currently only commentary has
  a real LLM hook) so ambiguous note-number placements can be resolved by an LLM.
- Add a RAG layer over the qualitative filing sections so AI Insights can answer free-text
  questions, not just narrate computed metrics.
- Multi-tenant the data model so this becomes a template for any Assiduous client, not just Senus.
- Replace the demo JWT auth with a production-grade auth provider.

## Deliverables

1. Live deployed app: _add Render frontend URL_
2. YouTube demo link: _add after recording_
3. GitHub repo link: [github.com/VirtualBeetle/senus-board-report](https://github.com/VirtualBeetle/senus-board-report)
4. One-page write-up: [`ONE_PAGER.md`](./ONE_PAGER.md)
