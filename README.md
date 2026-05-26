---
# === AUTHORITATIVE (human-edited; folder-context indexer never crosses the fence) ===
folder_name: frank-and-brittney-ai
mode: how-to
status: active
sensitivity: normal
ai_update_allowed: true
vault_project:
canonical: true
github_remote: https://github.com/jonsims/ai-survey
parent_area: "[[Ventures]]"
# === AUTO-MAINTAINED (folder-context indexer rewrites; do not hand-edit) ===
last_indexed:
content_hash:
file_count:
related_folders_auto: []
---

# AI Intake Survey

A short, editorial intake survey for AI consulting conversations — static HTML/CSS/JS (no framework, no build), hosted on GitHub Pages, posting to a Google Sheet via Apps Script. The folder is currently the home of the first variant ("Frank and Brittney"), but the repo + pattern are designed to be generic — `for-<client-slug>/` subfolders share the parent's `style.css` + `form.js`. *(Whether to rename this folder to match the broader pattern: see questions-for-jon-2026-05-26 #1.)*

## What's in here

- `index.html` — the **generic canonical form** (the reusable variant, tagged `v1.0`)
- `style.css` + `form.js` — shared design system + validation/submit (variants link to these via `../`)
- `for-frank-and-brittney/` — the first customized variant (`index.html` + `variant.css` burgundy accent)
- `apps-script/Code.gs` — backend code to paste into Apps Script editor (writes to Google Sheet)
- `PRD-analytics-demo.md`, `AUDIT.md`, `PLAN.md`, `RESEARCH-public-databases.md` — design + research docs
- `analytics/` + `datasets/` — analytics demo + public-database research artifacts
- `README.md` (this file)

## What's NOT here (lives elsewhere)

- **Deployed site** — `https://jonsims.github.io/ai-survey/` (GitHub Pages from the `jonsims/ai-survey` public repo)
- **Frank & Brittney deployed variant** — `https://jonsims.github.io/ai-survey/for-frank-and-brittney/`
- **Response data** — Google Sheet `AI Intake — Responses` (one row per submission, with a `client` column to filter by variant)
- **Apps Script deployment URL** — constant `APPS_SCRIPT_URL` at the top of `form.js` (and visible in the Apps Script console)
- **Client-specific anything** — per-variant changes are limited to `data-client="..."` + the `--accent*` CSS variables; no per-client data lives in this repo

## Related folders

- [[for-steve]] (sibling, not on disk under `~/Projects/` here) — `~/Projects/For Steve/`; this project inherits the editorial-academic design register from For Steve
- [[projects-dashboard]] — should pick this folder up once the corresponding vault `Projects/*.md` entry is created
- Future client variants — each is a `for-<slug>/` subfolder; max ~5 before migrating to query-param + JSON config (Phase B roadmap)

## Context

Jon's AI consulting work needed a low-friction client intake mechanism — something short, editorial in tone (matching the [For Steve](https://github.com/babsongenerator/babson-frontier-ai-case) design register), and shareable as a URL without authentication friction. The fix: a static HTML/CSS/JS intake form hosted on GitHub Pages, posting submissions to a Google Sheet via Apps Script. The "Frank and Brittney AI" project name reflects the *first* customized variant (their version of the form, with burgundy accent), but the canonical pattern is a generic reusable form (`index.html` at repo root) with per-client variants in subfolders (`for-<client-slug>/`) that share `style.css` + `form.js` from the parent.

## Decision

This folder holds the static-site source for the AI Intake Survey: generic + Frank & Brittney variant + the Google Apps Script backend code + the documentation (PRD-analytics-demo, AUDIT, PLAN, RESEARCH-public-databases) + analytics + datasets subfolders. **It does NOT hold** the deployed site (that lives at `https://jonsims.github.io/ai-survey/` via GitHub Pages from the `jonsims/ai-survey` public repo), the response data (lives in a Google Sheet named `AI Intake — Responses`, not in this folder), the Apps Script deployment URL (constant `APPS_SCRIPT_URL` at the top of `form.js` — also visible in the Apps Script console), or sensitive client data (each variant just changes the `data-client="..."` attribute + the `--accent` CSS variable; no per-client data lives here). Adding a new client variant means copying `for-frank-and-brittney/` → `for-<slug>/` and customizing 4 things; see "Adding a new client variant" below.

## Consequences

A single bug fix or design improvement to the generic form propagates to every variant automatically (variants reference shared `style.css` + `form.js` via `../`). The Google Sheet backend gives a simple queryable destination — filter by the `client` column to isolate one variant's submissions; export to CSV when needed. The cost is two-step Apps Script deployment ritual (every `Code.gs` change requires Deploy → Manage deployments → New version → Deploy; the URL stays the same), and a max-~5-clients folder pattern before it should migrate to query-param + JSON config (Phase B roadmap). The mobile-first design (16px+ inputs to prevent iOS Safari zoom-jump, 44px+ touch targets) means the form works well as a phone link — which is the most common share path. **Action item: this folder doesn't yet have a vault `Projects/*.md` entry; should be added so [[projects-dashboard]] picks it up.**

<!-- AI:BEGIN -->
## What's in here (auto)
*Auto-populated by the folder-context indexer on next reconcile.*

## Recent activity (auto, last 14 days)
*Auto-populated.*

## Cross-references (auto)
*Auto-populated.*
<!-- AI:END -->

---

## Quick reference

**Generic (canonical):** https://jonsims.github.io/ai-survey/
**Frank & Brittney variant:** https://jonsims.github.io/ai-survey/for-frank-and-brittney/

### Repo layout

```
ai-survey/
├── index.html                       # generic — the canonical reusable form
├── style.css                        # shared design system
├── form.js                          # shared validation + submit
├── apps-script/
│   └── Code.gs                      # backend (paste into Apps Script editor)
├── for-frank-and-brittney/
│   ├── index.html                   # variant — customized copy
│   └── variant.css                  # accent color override (burgundy)
└── README.md
```

The generic form is the canonical version (tagged `v1.0`). Variants live in subfolders, each with their own customized `index.html`, and reference the shared `style.css` and `form.js` via `../`. A bug fix to the generic propagates to every variant automatically.

### Adding a new client variant

1. Copy `for-frank-and-brittney/` to `for-<new-client-slug>/`.
2. Edit `index.html` in the new folder — change the masthead intro copy, the thank-you message, and the `data-client="..."` attribute on `<form>`.
3. (Optional) Edit `variant.css` to override the primary accent — only `--accent`, `--accent-dark`, `--accent-tint`, and `--accent-tint-strong` need to change.
4. Push. The variant is live at `https://jonsims.github.io/ai-survey/for-<slug>/`.
5. Filter the response Sheet by the `client` column to isolate that variant's submissions.

The shared `form.js` reads `data-client` from the `<form>` element and includes it in the submit payload, so all clients write to the same Sheet with a `client` column identifying which variant produced each row.

### One-time setup (already done; documented for future Jons)

#### 1. Create the response Sheet

1. Go to [sheets.new](https://sheets.new) and create a Google Sheet.
2. Name it `AI Intake — Responses`.
3. Copy the **Sheet ID** from the URL — the long string between `/d/` and `/edit`.

#### 2. Wire up the Apps Script backend

1. In the Sheet: **Extensions → Apps Script**.
2. Delete the boilerplate and paste the contents of [`apps-script/Code.gs`](apps-script/Code.gs).
3. Replace the `SHEET_ID` constant at the top with your Sheet ID.
4. Save (⌘S). Name the project `AI Intake Backend`.
5. **Deploy → New deployment**. Click the gear → **Web app**. Set:
   - **Description:** `v1`
   - **Execute as:** `Me`
   - **Who has access:** `Anyone`
6. Click **Deploy**, accept the Google permissions prompt.
7. Copy the **Web app URL** that ends in `/exec`.

#### 3. Point the form at the backend

Open [`form.js`](form.js) and paste the Web app URL into the constant at the top:

```js
const APPS_SCRIPT_URL = "https://script.google.com/macros/s/.../exec";
```

#### 4. Deploy to GitHub Pages

```bash
gh repo create jonsims/ai-survey --public --source=. --push
```

Then on GitHub: **Settings → Pages → Source: Deploy from a branch → `main` / `(root)` → Save.**

### Iterating

- **Test without spamming the Sheet:** clear `APPS_SCRIPT_URL` in `form.js` and submit — payload prints to the browser console.
- **Add or rename a field:** edit `index.html` (the `name` attribute is what matters), then add the new key to `HEADERS` in [`apps-script/Code.gs`](apps-script/Code.gs) and (if it's a multi-select) to `MULTI_SELECTS` in [`form.js`](form.js).
- **Apps Script changes don't auto-update.** After every edit to `Code.gs` you have to **Deploy → Manage deployments → ✏️ → New version → Deploy** for the live form to see the change. The URL stays the same.
- **Multi-select values** arrive in the Sheet as `value1; value2; value3` — joined by the backend.

### Design

Editorial / "McKinsey-BCG-federal-report" register, lifted from the [For Steve](https://github.com/babsongenerator/babson-frontier-ai-case) project. IBM Plex Serif body, IBM Plex Sans headings, IBM Plex Mono accents. Off-white background, white cards with a thin colored left stripe cycling through three editorial accents (forest teal `#0F5F4D` primary, gold `#B07A2A`, slate navy `#3F4F75`).

Mobile-first — base styles target phone, media queries scale up. All inputs are 16px+ on mobile to prevent iOS Safari's zoom-jump. Touch targets are 44px+ tall.

To re-theme a variant: override the four `--accent*` CSS custom properties in `variant.css`. The section-cycle secondary accents stay constant; only the primary changes.

### Roadmap (Phase B — additive, optional)

- One-section-per-card with smooth scroll between cards
- Thin progress bar that fills as sections complete
- Sticky prev/next pagination on phone
- Save-draft to `localStorage` so partial responses survive a refresh
- Reader-controlled font-size scale (older-eyes-friendly)
- Optional email-receipt to the respondent
- If client count grows past ~5, migrate from folder-per-variant to a query-param + JSON-config pattern
