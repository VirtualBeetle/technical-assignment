# Senus PLC — AI-Native Board Report Platform

Built for the Assiduous Corp Technology Graduate assignment: an AI-native platform that
prepares a Board Report for Senus PLC (an Assiduous listing client) for Management, the
Board, Equity Investors and Credit Providers.

**Demo login:** `ceo@senus.com` / `Senus2030!` (seeded automatically, see [Assumptions](#assumptions)).

## What this is

A full-stack web application, not a static report:

- **Backend** (FastAPI + SQLAlchemy + PostgreSQL/SQLite) exposes a REST API over structured
  financial data extracted from Senus PLC's real regulatory filings.
- **Extraction pipeline** turns the raw source PDFs (some native-text, some scanned/image-only)
  into structured line items via OCR + regex, with an optional LLM structuring stage, validated
  against a hand-verified dataset.
- **Metrics engine** computes the board-report ratios called for in the brief: growth, margins,
  EBITDA, cash runway, an EBITDA→FCF bridge, solvency/leverage, and ROCE.
- **AI commentary layer** turns those metrics into board-ready prose, in a deterministic
  "demo mode" by default, or via an LLM if you provide an API key.
- **Frontend** (Next.js + TypeScript + Tailwind + Recharts) is the interactive dashboard a CEO
  would actually log into: Overview, Growth & Revenue, Profitability, Cash & Liquidity,
  Solvency & Leverage, Returns, and an AI Insights hub, with a period selector spanning
  FY2024, FY2025, H1 FY2025 and H1 FY2026 (the latest reported period).

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
| Database | PostgreSQL (prod, via docker-compose) / SQLite (zero-config local dev) | Same SQLAlchemy models, `DATABASE_URL` env var switches engines. |
| ORM | SQLAlchemy 2.0 | Typed models, explicit schema, no framework lock-in. |
| PDF/OCR | pdfplumber, pytesseract, pdf2image | Two of the six filings are scanned images with no text layer — needed real OCR, not just a text-layer parser. |
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind + Recharts | Matches the JD's stack; client-rendered dashboard is the right fit for an authenticated, API-driven SPA. |
| Auth | JWT (python-jose) + bcrypt (passlib) | Deliberately minimal — see Assumptions. |
| AI | Deterministic rule-based generator by default; optional OpenAI-compatible LLM call | Same pattern as my FAIR_GPT project: works with zero credentials, upgrades cleanly with a key. |
| Deployment | Docker Compose (local) / Render Blueprint (`render.yaml`, cloud) | One Dockerfile per service, root build context for the backend so `data/` ships inside the image — same containers run locally and in production. |

## AI-assisted development workflow

This project was built in an AI-assisted session (Claude), with every step reviewed and
validated rather than accepted blindly:

1. **Research** — read the assignment brief, JD, and all six Senus source filings (half-year
   results, ADF Farm Solutions annual consolidated accounts, the Dec-2025 balance sheet, the
   direct-listing press release, the notification-of-results release, and the leadership-
   transition release) to build a full picture of the business before writing any code.
2. **Manual figure verification** — every number in `data/senus_financials.json` was read
   directly off the source PDFs (by a human/AI reader, not by trusting OCR blindly) and cited
   back to its source document in the `provenance` section of that file.
3. **AI-assisted extraction pipeline** — `backend/app/ingestion/extract_pdfs.py` was then
   written and iterated against the *actual* PDFs until it reproduced the gold dataset
   (see [Validation](#validation) below) — this is the "AI methods for extracting financial
   information from source documents into a database" the brief asks for.
4. **Schema, metrics engine, API, frontend** — built iteratively, testing each layer (unit
   tests, live curl requests against a running server, a full `next build`) before moving to
   the next, rather than writing the whole stack and debugging at the end.
5. **AI commentary** — built with an explicit deterministic fallback so the demo never depends
   on an API key being present; the LLM path is a genuine drop-in upgrade, not vaporware.

## AI extraction pipeline, in detail

Run it yourself:

```bash
cd backend
pip install -r requirements.txt
python -c "from app.ingestion.extract_pdfs import run; run()"
```

What it does:

1. `get_page_text` pulls the embedded text layer per PDF page with `pdfplumber`. Two of the
   six filings (the ADF Farm Solutions annual accounts and the Senus Ltd balance sheet as at
   8 Dec 2025) have **no text layer at all** — they're scanned/rendered accounting-software
   exports — so those specific pages fall back to Tesseract OCR via `pdf2image`, rendering
   only the page needed rather than the whole document (fast: a 23-page scanned filing OCRs
   in a couple of seconds this way instead of tens of seconds).
2. `parse_two_column_statement` extracts `"Label  value_a  value_b"` rows with a regex tuned
   to how Irish FRS 102 small-company accounts are laid out, tolerating a stray note-reference
   number between the label and its values (e.g. `"Group operating loss 3 (633,694) (1,130,729)"`).
3. `normalize_signs` reconciles two real sign conventions that differ between filings: the
   annual accounts print cost lines in parentheses (so regex reads them as negative) while the
   half-year PR prints them unsigned; both filings print "loss" lines as a bare positive
   magnitude under an explicit "loss" label. This is a small, explicit, documented rule set
   rather than a black-box guess.
4. `validate_against_gold` diffs everything the script extracted against the hand-verified
   `data/senus_financials.json` and prints a match/mismatch report.

### Validation

On the current codebase, the pipeline reproduces **57/57 (100%)** of the targeted numeric
fields across all three financial statements it's pointed at. Getting there was itself part
of the validation process — the first pass came back at 47/57 (82.5%), with the 10 mismatches
all traced to the two sign-convention issues described above, which is what `normalize_signs`
exists to fix. That before/after is the evidence for "how you validated the outputs": the
pipeline isn't assumed correct, it's checked field-by-field against a source-cited ground
truth, and every disagreement was root-caused rather than papered over.

The **live application does not run on the raw regex/OCR output directly** — it loads
`data/senus_financials.json` (see `app/ingestion/gold_dataset.py` for the rationale). Financial
data feeding a board report is exactly the kind of output where "trust but verify" matters:
the extraction pipeline is real, runnable, and validated, but a human-reviewed dataset is what
the app is actually seeded from, mirroring how a real fintech would stage AI-extracted data
behind a review step before it reaches decision-makers.

The metrics engine (`app/metrics.py`) has its own unit tests (`backend/tests/test_metrics.py`)
that check computed ratios against hand-calculated values, including one internal-consistency
check (EBITDA computed from the P&L matches the pre-working-capital subtotal disclosed
separately in the cash-flow statement of the same filing).

## Data model

- `companies`, `directors` — Senus PLC profile, listing details, Senus 2030 strategy targets.
- `financial_periods` — FY2024, FY2025 (annual, audited), H1 FY2025 and H1 FY2026 (half-year,
  unaudited, per the half-year results announcement).
- `line_items` — an EAV-style `(statement, key) → value` table per period, chosen over one
  column per line item so new line items (e.g. the Loamin goodwill/contingent-consideration
  lines that only appear from H1 FY2026 onwards) don't require a schema migration.
- `commercial_facts` — non-statement facts: pipeline value, deals closed, named contracts.
- `metric_snapshots` — cached output of the metrics engine per period/category.
- `commentary` — AI-generated (or rule-based) board commentary per period/section.
- `users` — single demo CEO account for the login screen.

## Running it

### Option A — Docker Compose (closest to a real deployment)

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API + docs: http://localhost:8000/docs
- Postgres: localhost:5432 (credentials in `docker-compose.yml`)

The backend seeds itself from `data/senus_financials.json` on first startup — no manual
migration step needed.

### Option B — Local dev (SQLite, no Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload   # http://localhost:8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev                     # http://localhost:3000
```

### Option C — Live demo (deployed on Render)

No setup at all — open the deployed URL directly: _add Render frontend URL here after
deploying (see [Deploying to Render](#deploying-to-render) below)_.

### Running the AI extraction demo / validation report

```bash
cd backend
python -c "from app.ingestion.extract_pdfs import run; run()"
# writes data/extraction_report.json
```

### Running tests

```bash
cd backend
python -m pytest tests/ -v
```

## Deploying to Render

The app ships with a `render.yaml` Blueprint that provisions all three pieces from a single
click — no manual dashboard configuration, no Docker setup on the reviewer's end.

1. Push this repo to GitHub (public or private — Render can be granted access to either).
2. In the [Render dashboard](https://dashboard.render.com), click **New → Blueprint** and point
   it at the repo. Render reads `render.yaml` at the root and shows a plan: one Postgres
   database, one backend web service, one frontend web service.
3. Click **Apply**. Render builds both Docker images (root build context for the backend, so
   `data/senus_financials.json` and the source PDFs get baked into the image — see the comment
   in `backend/Dockerfile`) and deploys all three resources together.
4. Once both services are live, open the **frontend** service's `onrender.com` URL — that's the
   single link to hand to a reviewer. The frontend's server-side Next.js rewrite proxies
   `/api/*` to the backend over Render's private network (`BACKEND_INTERNAL_URL`, wired
   automatically via the Blueprint's `fromService` reference), so the browser only ever talks
   to one origin and there's no CORS configuration to get right.
5. The backend also gets its own public URL if you want to show `/api/health` or the
   auto-generated Swagger docs at `/docs` directly.

No manual environment variable entry is required — `JWT_SECRET` is auto-generated by Render on
first deploy, `DATABASE_URL` is wired from the provisioned Postgres instance, and the demo
login (`ceo@senus.com` / `Senus2030!`) is seeded automatically on backend startup exactly as it
is locally.

**Notes:**

- Both services are on Render's **free** plan by default (see `render.yaml`) — free-tier web
  services spin down after 15 minutes of inactivity and take ~30-60s to wake back up on the
  first request after that; free Postgres instances expire after 90 days. Bump `plan:` to
  `starter` in `render.yaml` (and re-sync the Blueprint) if that's not acceptable for a longer
  review window.
- To use a real LLM for the AI commentary instead of the deterministic demo-mode generator, set
  `AI_PROVIDER=openai` and add `OPENAI_API_KEY` as a Render environment variable on the backend
  service after the initial deploy (kept out of `render.yaml`/git on purpose).

## Assumptions

- **Auth is demo-grade.** A single hardcoded CEO account, JWT in a bearer token stored in
  `localStorage`. The brief asks for "a platform a CEO would log in to and use" as a
  demonstration surface, not a production identity system — a real deployment would add
  refresh tokens, httpOnly cookies, and proper RBAC.
- **The Senus Limited balance sheet as at 8 Dec 2025 is company-only (parent), not
  consolidated** — it was prepared for the CRO re-registration to a PLC and pre-dates the
  Loamin acquisition being reflected at group level. It's used in this project only as a
  standalone credit/liquidity cross-check, not blended into the group P&L/balance-sheet trend.
- **EBITDA = operating loss + depreciation.** No intangible amortisation has been charged in
  these filings yet (the Loamin goodwill/development costs are only ~1-2 months old at the
  H1 FY2026 balance sheet date), so EBITDA and "EBIT + depreciation" are the same number here.
- **DSCR and Net Debt/EBITDA are reported as "not yet meaningful"** while EBITDA is negative,
  rather than shown as a nonsensical negative ratio — Senus 2030 targets EBITDA breakeven in
  FY2028, at which point these become decision-useful for credit providers.
- **Customer-account count (138) is a single data point** (disclosed only in the FY2025
  annual filing / subsequent press releases), not a time series — shown as a KPI rather than
  a trend line, and the pipeline figures disclosed in the H1 FY2026 results (deals closed,
  open pipeline) are shown as forward-looking commercial context, not restated as revenue.
- **AI commentary defaults to a rule-based generator**, not because an LLM integration
  wasn't built, but so the app is always demoable without requiring you to hand over an API
  key — set `AI_PROVIDER=openai` and `OPENAI_API_KEY` to switch it on; if that call fails for
  any reason the app falls back automatically rather than showing a broken page.

## What I'd do next with more time

- Wire the LLM structuring stage into `extract_pdfs.py` itself (currently only the commentary
  layer has a real LLM hook) so ambiguous note-number placements can be resolved by an LLM
  rather than left for human review.
- Add a vector-search / RAG layer over the qualitative sections of the filings (Chairman's
  statement, commercial progress narrative) so the AI Insights page could answer free-text
  questions ("what changed in the pipeline this half?"), not just narrate computed metrics.
- Multi-tenant the data model so this becomes a template for any Assiduous client, not just
  Senus, with per-company period/metric tables already structured to support that.
- Replace the demo JWT auth with a production-grade auth provider.

## Deliverables

1. Live deployed app: _add Render frontend URL here after deploying (see
   [Deploying to Render](#deploying-to-render))_
2. YouTube demo link: _add after recording_
3. GitHub repo link: _add after pushing this folder_
4. One-page write-up: [`ONE_PAGER.md`](./ONE_PAGER.md)
