# Senus PLC Board Report — One-Page Write-Up

What it is: an AI-native full-stack platform that turns Senus PLC's public filings into
an interactive Board Report for Management, the Board, Equity Investors and Credit Providers —
covering Growth & Revenue, Profitability, Cash & Liquidity, Solvency & Leverage, Returns, and
AI-generated commentary, across FY2024, FY2025, H1 FY2025 and H1 FY2026 (the latest reported
period).

Why it's built this way

Senus is a pre-EBITDA-breakeven, recently-listed micro-cap that just completed its first
acquisition (Loamin) and a direct listing. That context shaped three deliberate decisions:

- DSCR and Net Debt/EBITDA are flagged "not yet meaningful" rather than shown as a nonsense
  negative ratio — Senus 2030 targets EBITDA breakeven in FY2028; a credit provider needs to
  know that context, not a misleading number.
- The €850k Loamin contingent consideration is called out explicitly — it's the single
  biggest driver of the negative net-current-assets position in the H1 FY2026 balance sheet,
  but it's performance-linked and non-cash unless targets are met. A board report that let that
  number scare a reader without the caveat would be worse than no report at all.
- Two of the six source filings are scanned images with no text layer. Rather than skip them
  or hand-key the numbers with no pipeline behind them, the extraction pipeline does real OCR
  (Tesseract) for those specific documents and is validated field-by-field against a
  hand-verified dataset (57/57 fields matched after fixing two genuine sign-convention bugs
  the validation surfaced — see README "Validation").

Architecture: FastAPI + SQLAlchemy + PostgreSQL (SQLite for zero-config local dev) on the
backend; Next.js + TypeScript + Tailwind + Recharts on the frontend; a JSON gold dataset as the
seeded source of truth, with a genuinely runnable OCR/regex extraction pipeline validated
against it. Full detail in `README.md`.

AI-native aspects:
1. An OCR + regex extraction pipeline for scanned/native-text PDFs, with a documented sign-
   normalization layer and an automated validation report against hand-verified figures.
2. An AI commentary layer that turns computed metrics into board-ready prose — deterministic
   by default (auditable, zero-credential demo mode) with a drop-in OpenAI upgrade path.

How I validated the outputs: unit tests on the metrics engine against hand-calculated
ratios (including an internal-consistency check between the P&L and cash-flow statement of
the same filing); a field-by-field extraction validation report; and a full `next build` with
TypeScript strict mode to catch integration bugs between frontend and API before runtime.

Tools used: Claude (AI-assisted development, throughout), FastAPI, SQLAlchemy, pdfplumber,
Tesseract OCR, Next.js, Tailwind, Recharts, pytest, Docker Compose, GitHub Actions.
