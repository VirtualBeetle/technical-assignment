# Senus PLC — AI-Native Board Report Platform

Built for the Assiduous Corp Technology Graduate assignment: an AI-native Board Report
platform for Senus PLC, for Management, the Board, Equity Investors and Credit Providers.

**Live demo:** [https://senus-board-report-frontend.onrender.com/dashboard](https://senus-board-report-frontend.onrender.com/dashboard)
**Demo login:** `ceo@senus.com` / `Senus2030!`
**GitHub:** [github.com/VirtualBeetle/technical-assignment](https://github.com/VirtualBeetle/technical-assignment)

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
| Auth | JWT (python-jose) + bcrypt (passlib) | Deliberately minimal, demo-grade auth — single hardcoded account, JWT in `localStorage`. |
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

- **Live demo** — [https://senus-board-report-frontend.onrender.com/dashboard](https://senus-board-report-frontend.onrender.com/dashboard), no setup needed.
- **Docker Compose** — `docker compose up --build` → frontend `localhost:3000`, backend `localhost:8000/docs`.
- **Local dev, no Docker** — `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`,
  then in another terminal `cd frontend && npm install && npm run dev`.
- **Extraction validation report** — `cd backend && python -c "from app.ingestion.extract_pdfs import run; run()"`
- **Tests** — `cd backend && python -m pytest tests/ -v`

## Features

- Full-stack app — FastAPI backend, Next.js dashboard, PostgreSQL/SQLite storage, JWT auth.
- OCR + regex extraction pipeline, validated 57/57 (100%) against a hand-verified dataset.
- Metrics engine covering all five board-report categories: Growth & Revenue, Profitability,
  Cash & Liquidity, Solvency & Leverage, Returns — with an EBITDA→FCF bridge and cash runway.
- AI commentary layer — deterministic rule-based generator by default, drop-in LLM upgrade
  with an API key, automatic fallback if the LLM call fails.
- Period selector spanning FY2024, FY2025, H1 FY2025, and H1 FY2026, recomputing metrics live.
- One codebase, two deploy paths — `docker compose up --build` locally, or a Render Blueprint
  (`render.yaml`) for a one-click cloud deploy, using the same Docker images both times.
- GitHub Actions CI — runs the backend test suite and re-validates the extraction pipeline on
  every push.
- Unit-tested metrics engine, including an internal-consistency check between the P&L and
  cash-flow statement.

## Deliverables

1. Live deployed app: [https://senus-board-report-frontend.onrender.com/dashboard](https://senus-board-report-frontend.onrender.com/dashboard)
2. YouTube demo link: _add after recording_
3. GitHub repo link: [github.com/VirtualBeetle/technical-assignment](https://github.com/VirtualBeetle/technical-assignment)
4. One-page write-up: [`ONE_PAGER.md`](./ONE_PAGER.md)
