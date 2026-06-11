# Frank and Brittney AI

## What this is

Two-track project for an AI consulting engagement with early-stage clients:

1. **AI Intake Survey** (shipped, locked at v1.0) — static HTML form at `jonsims.github.io/ai-survey/for-frank-and-brittney/`. Posts to a Google Sheet via Apps Script. IBM Plex editorial aesthetic, folder-per-client variant pattern.

2. **Analytics Dashboard / Rent Planner** (active, demo stage) — interactive HTML dashboard at `for-frank-and-brittney/demo/v2/index.html` demonstrating AI-powered data analytics on federal housing data + a dummy property portfolio. Named "Prestige Worldwide" (Step Brothers reference).

## Stack

- Intake survey: vanilla HTML/CSS/JS, Google Apps Script backend
- Analytics: Python 3.11 (`analytics/.venv`), pandas, DuckDB, matplotlib, Plotly.js, Marimo (optional interactive version)
- Dashboard: self-contained HTML + embedded JSON + Plotly.js CDN. No backend required at runtime.
- Data: 5 federal datasets in `datasets/` (HUD LIHTC, FMR, Income Limits, QCT/DDA, IRS Migration) + dummy portfolio in `datasets/dummy/`

## Key paths

| What | Where |
|---|---|
| Live dashboard (v2) | `for-frank-and-brittney/demo/v2/index.html` |
| Analytics scripts | `analytics/01_*.py` through `04_*.py` |
| Shared data loaders | `analytics/lib.py` |
| Dummy portfolio generator | `analytics/generate_dummy_portfolio.py` |
| Dashboard data export | `analytics/export_v2_json.py` |
| Dashboard builder (v3) | `analytics/build_v3.py` |
| PRD | `PRD-analytics-demo.md` (symlink to ~/.Codex/plans/) |
| Research catalog | `RESEARCH-public-databases.md` (symlink) |
| Emma's Estates design reference | `for-frank-and-brittney/demo/emmas-estates/` |
| Marimo interactive dashboard | `analytics/dashboard.py` (port 2718) |

## Dashboard tabs (v2)

1. **Rent Planner** — editable per-property rent increase table with bulk apply, AMI ceiling enforcement, live KPIs, CSV export
2. **Properties** — table/grid toggle with type-specific SVG illustrations, click-for-detail modal
3. **Portfolio** — KPI summary + composition charts
4. **Market** — FMR trajectory + preservation pipeline from federal data
5. **Rent Decision** — single-property deep-dive with waterfall chart, expense modeling, slider-driven projections
6. **? Guide** — 8-step how-to for the annual rent-increase process, with clickable tab links and contextual banners

## Privacy

Client-identifying information (names, sector, geography) is stripped from all shareable docs (PRD, README, plans). See global memory `feedback_client-privacy-in-docs.md`. The dashboard itself uses fictional data ("Prestige Worldwide") for demo purposes.

## Data pipeline

```
generate_dummy_portfolio.py  →  datasets/dummy/{portfolio,unit_mix}.csv
export_v2_json.py            →  analytics/output/v2_data.json
build_v3.py (or direct edit) →  for-frank-and-brittney/demo/v2/index.html
```

To rebuild: `cd analytics && .venv/bin/python export_v2_json.py && .venv/bin/python build_v3.py`

The v2 dashboard HTML is now maintained by direct edit (not rebuilt from the builder) since UX iterations are faster inline.

## Design system

Heritage forest (#1F4A3D) + brass (#B07A2A) + slate (#3F4F75) accents on neutral gray (#F7FAFC). IBM Plex Sans for everything, IBM Plex Mono for numbers. Card-based layout, no scroll on data tabs. Optimized for older users on desktop monitors — 17px base font, tight column spacing, large modal text.

## Glossary

12 acronyms (AMI, LIHTC, DSCR, NOI, FMR, HUD, MHP, OpEx, CapEx, FY, IRS, CSV) are auto-wrapped with dotted-underline click-to-define tooltips throughout the dashboard.
