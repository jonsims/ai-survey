# AI Intake Survey

A short, beautiful intake survey for AI consulting conversations. Static HTML/CSS/JS — no framework, no build step. Posts responses to a Google Sheet via a Google Apps Script Web App.

**Live (once deployed):** `https://jonsims.github.io/ai-survey`

## What's in here

```
ai-survey/
├── index.html         # the form — 8 sections, ~12 fields
├── style.css          # editorial design system (IBM Plex, McKinsey/BCG register)
├── form.js            # validation + submit
├── apps-script/
│   └── Code.gs        # paste this into Apps Script (the backend)
└── README.md
```

## One-time setup (~15 minutes)

### 1. Create the response Sheet

1. Go to [sheets.new](https://sheets.new) and create a Google Sheet.
2. Name it `AI Intake — Responses`.
3. Copy the **Sheet ID** from the URL — it's the long string between `/d/` and `/edit`:
   ```
   https://docs.google.com/spreadsheets/d/{SHEET_ID_HERE}/edit
   ```

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

(If you leave it blank, the form runs in local-dev mode — submit just logs the payload to the browser console. Useful for design iteration.)

### 4. Deploy to GitHub Pages

```bash
git init
git add .
git commit -m "Initial commit"
gh repo create jonsims/ai-survey --public --source=. --push
```

Then on GitHub: **Settings → Pages → Source: Deploy from a branch → `main` / `(root)` → Save.**

A minute or two later the form is live at `https://jonsims.github.io/ai-survey`.

## Iterating

- **Test without spamming the Sheet:** clear `APPS_SCRIPT_URL` in `form.js` and submit — payload prints to the browser console.
- **Add or rename a field:** edit `index.html` (the `name` attribute is what matters), then add the new key to `HEADERS` in both `apps-script/Code.gs` and (if it's a multi-select) `MULTI_SELECTS` in `form.js`.
- **Apps Script changes don't auto-update.** After every edit to `Code.gs` you have to **Deploy → Manage deployments → ✏️ → New version → Deploy** for the live form to see the change. The URL stays the same.
- **Multi-select values** arrive in the Sheet as `value1; value2; value3` — joined by the backend.

## Design

Editorial / "McKinsey-BCG-federal-report" register, deliberately echoing the
[For Steve](https://github.com/babsongenerator/babson-frontier-ai-case) project. IBM Plex Serif body, IBM Plex Sans headings, a single calm forest-teal accent (`#0F5F4D`), off-white background, charcoal topbar with uppercase tracked label.

Mobile-first — base styles target phone, media queries scale up. All inputs are 16px+ on mobile to prevent iOS Safari's zoom-jump. Touch targets are 44px+ tall.

To re-theme: edit the CSS custom properties at the top of `style.css`. The accent color is one variable change.

## Roadmap (Phase B — additive, optional)

- One-section-per-card with smooth scroll between cards
- Thin progress bar that fills as sections complete
- Sticky prev/next pagination on phone
- Save-draft to `localStorage` so partial responses survive a refresh
- Reader-controlled font-size scale (older-eyes-friendly)
- Optional email-receipt to the respondent
