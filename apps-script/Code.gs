/**
 * AI Intake Survey — Google Apps Script backend
 * Paste this into a Google Apps Script project bound to (or referencing)
 * the response spreadsheet. Deploy as a Web App; that URL goes into form.js.
 *
 * Setup, in three steps:
 *   1. Create a Google Sheet titled "AI Intake — Responses".
 *      The script will auto-create the header row on first submit.
 *   2. Replace SHEET_ID below with the spreadsheet's ID (it's the long
 *      string in the URL between /d/ and /edit).
 *   3. Deploy → New deployment → Type: Web app.
 *        Execute as:        Me  (your account)
 *        Who has access:    Anyone
 *      Copy the resulting Web App URL into form.js as APPS_SCRIPT_URL.
 *
 * Multi-selects come in as arrays; they get joined with "; " for the cell.
 * The form posts as text/plain (to avoid CORS preflight), so the JSON
 * is in e.postData.contents.
 */

const SHEET_ID = 'PASTE_SHEET_ID_HERE';

const HEADERS = [
  'timestamp',
  'name',
  'role',
  'ai_familiarity',
  'ai_concepts_known',
  'tools_used',
  'anthropic_experience',
  'tools_shortfalls',
  'goals',
  'specific_situation',
  'regulated_data',
  'tech_comfort',
  'tech_activities',
  'specialized_software',
  'other_software',
  'tech_curiosity',
  'learning_openness',
  'pain_points',
  'success_six_months',
  'anything_else',
  'client', // appended last so existing rows align cleanly; identifies the variant the response came from ("generic", "frank-and-brittney", future client slugs)
];

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheets()[0];

    // Seed the header row if the sheet is empty.
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(HEADERS);
      sheet.setFrozenRows(1);
    }

    const row = HEADERS.map(h => {
      if (h === 'timestamp') return new Date().toISOString();
      const v = data[h];
      if (Array.isArray(v)) return v.join('; ');
      return v == null ? '' : String(v);
    });

    sheet.appendRow(row);

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/* Optional: a doGet that returns a tiny health check so you can hit the
   Web App URL in a browser and see it's wired up. */
function doGet() {
  return ContentService
    .createTextOutput('AI Intake Survey endpoint — POST JSON to submit a response.')
    .setMimeType(ContentService.MimeType.TEXT);
}
