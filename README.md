# AI Intake Survey

A short, editorial intake survey for AI consulting conversations. Static HTML/CSS/JS — no framework, no build step. Posts responses to a Google Sheet via a Google Apps Script Web App.

**Generic (canonical):** https://jonsims.github.io/ai-survey/
**Frank & Brittney variant:** https://jonsims.github.io/ai-survey/for-frank-and-brittney/

## What's in here

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

## Adding a new client variant

1. Copy `for-frank-and-brittney/` to `for-<new-client-slug>/`.
2. Edit `index.html` in the new folder — change the masthead intro copy, the thank-you message, and the `data-client="..."` attribute on `<form>`.
3. (Optional) Edit `variant.css` to override the primary accent — only `--accent`, `--accent-dark`, `--accent-tint`, and `--accent-tint-strong` need to change.
4. Push. The variant is live at `https://jonsims.github.io/ai-survey/for-<slug>/`.
5. Filter the response Sheet by the `client` column to isolate that variant's submissions.

The shared `form.js` reads `data-client` from the `<form>` element and includes it in the submit payload, so all clients write to the same Sheet with a `client` column identifying which variant produced each row.

## One-time setup (already done; documented for future Jons)

### 1. Create the response Sheet

1. Go to [sheets.new](https://sheets.new) and create a Google Sheet.
2. Name it `AI Intake — Responses`.
3. Copy the **Sheet ID** from the URL — the long string between `/d/` and `/edit`.

### 2. Wire up the Apps Script backend

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

### 3. Point the form at the backend

Open [`form.js`](form.js) and paste the Web app URL into the constant at the top:

```js
const APPS_SCRIPT_URL = "https://script.google.com/macros/s/.../exec";
```

### 4. Deploy to GitHub Pages

```bash
gh repo create jonsims/ai-survey --public --source=. --push
```

Then on GitHub: **Settings → Pages → Source: Deploy from a branch → `main` / `(root)` → Save.**

## Iterating

- **Test without spamming the Sheet:** clear `APPS_SCRIPT_URL` in `form.js` and submit — payload prints to the browser console.
- **Add or rename a field:** edit `index.html` (the `name` attribute is what matters), then add the new key to `HEADERS` in [`apps-script/Code.gs`](apps-script/Code.gs) and (if it's a multi-select) to `MULTI_SELECTS` in [`form.js`](form.js).
- **Apps Script changes don't auto-update.** After every edit to `Code.gs` you have to **Deploy → Manage deployments → ✏️ → New version → Deploy** for the live form to see the change. The URL stays the same.
- **Multi-select values** arrive in the Sheet as `value1; value2; value3` — joined by the backend.

## Design

Editorial / "McKinsey-BCG-federal-report" register, lifted from the [For Steve](https://github.com/babsongenerator/babson-frontier-ai-case) project. IBM Plex Serif body, IBM Plex Sans headings, IBM Plex Mono accents. Off-white background, white cards with a thin colored left stripe cycling through three editorial accents (forest teal `#0F5F4D` primary, gold `#B07A2A`, slate navy `#3F4F75`).

Mobile-first — base styles target phone, media queries scale up. All inputs are 16px+ on mobile to prevent iOS Safari's zoom-jump. Touch targets are 44px+ tall.

To re-theme a variant: override the four `--accent*` CSS custom properties in `variant.css`. The section-cycle secondary accents stay constant; only the primary changes.

## Roadmap (Phase B — additive, optional)

- One-section-per-card with smooth scroll between cards
- Thin progress bar that fills as sections complete
- Sticky prev/next pagination on phone
- Save-draft to `localStorage` so partial responses survive a refresh
- Reader-controlled font-size scale (older-eyes-friendly)
- Optional email-receipt to the respondent
- If client count grows past ~5, migrate from folder-per-variant to a query-param + JSON-config pattern
