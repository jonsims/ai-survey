/*  AI Intake Survey — form.js
    Validates required fields, gathers responses, posts to Apps Script,
    shows inline thank-you. Phase A (MVP) — no progressive disclosure yet.
    --------------------------------------------------------------------- */

/* 1. Paste the deployed Apps Script Web App URL here.
      Leave as empty string during local development — submit will then
      log the payload to the console instead of POSTing, so you can
      design without round-tripping to Google. */
const APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzwvI0d52ZDZaYBPF3qzT8z_i-Swakc1zvjJXPtGhcKdjYmcsQAA7yUYgRWplNE_Mv_/exec";

/* Fields that must be filled for the form to submit. Keep this list short
   — better to capture a partial response than nag people away. */
const REQUIRED = ["name", "ai_familiarity", "tech_comfort"];

/* Multi-select fields — values get collected as arrays and joined with
   "; " on the server side. */
const MULTI_SELECTS = new Set([
  "ai_concepts_known",
  "tools_used",
  "goals",
  "regulated_data",
  "tech_activities",
  "specialized_software",
  "learning_openness",
]);

const form    = document.getElementById("survey");
const thanks  = document.getElementById("thanks");
const errorEl = form.querySelector(".submit-error");
const submitBtn = form.querySelector(".submit-btn");

form.addEventListener("submit", onSubmit);

/* Clear field-error state as the user fills the field back in. */
form.addEventListener("input",  clearFieldError);
form.addEventListener("change", clearFieldError);

function onSubmit(ev) {
  ev.preventDefault();

  clearAllErrors();
  const data = collect(form);

  const missing = REQUIRED.filter(n => isEmpty(data[n]));
  if (missing.length) {
    missing.forEach(markFieldError);
    showError("Missing a few answers — see the highlighted questions above.");
    scrollToFirstError();
    return;
  }

  setSubmitting(true);

  send(data)
    .then(() => showThanks(data.name))
    .catch((err) => {
      console.error("[ai-survey] submit failed:", err);
      showError("Couldn't send right now. Email me your answers instead, or try again in a minute.");
      setSubmitting(false);
    });
}

/* Gather all named fields into a plain object. Multi-selects become arrays.
   Also picks up data-client from the form element so the backend knows
   which variant the response came from. */
function collect(formEl) {
  const out = {};
  const fd = new FormData(formEl);
  for (const [k, v] of fd.entries()) {
    if (MULTI_SELECTS.has(k)) {
      (out[k] ||= []).push(v);
    } else {
      out[k] = (v ?? "").toString().trim();
    }
  }
  // Make sure multi-select keys exist (as empty arrays) even when nothing
  // was checked, so the Sheet always has a clean blank cell.
  MULTI_SELECTS.forEach(k => { if (!(k in out)) out[k] = []; });

  // Variant identifier — set per page via data-client on the <form>.
  // Defaults to "generic" if absent.
  out.client = formEl.dataset.client || "generic";

  return out;
}

function isEmpty(v) {
  if (Array.isArray(v)) return v.length === 0;
  return v == null || String(v).trim() === "";
}

/* Apps Script Web App + cross-origin POST: avoid a CORS preflight by
   sending as text/plain. Apps Script reads e.postData.contents either way. */
function send(data) {
  const body = JSON.stringify(data);

  if (!APPS_SCRIPT_URL) {
    // Local-dev mode: log and resolve so the UX is fully testable.
    console.log("[ai-survey] payload (no APPS_SCRIPT_URL set):", data);
    return new Promise(r => setTimeout(r, 400));
  }

  return fetch(APPS_SCRIPT_URL, {
    method: "POST",
    mode: "no-cors",                  // accept opaque response; row still lands
    headers: { "Content-Type": "text/plain;charset=utf-8" },
    body,
  });
}

/* ------------------------------ errors ----------------------------------- */

function markFieldError(name) {
  const node = form.querySelector(`[name="${name}"]`);
  if (!node) return;
  // For radios/checkboxes the visible "field" is the wrapping fieldset;
  // for text/textarea it's the closest .field.
  const wrapper = node.closest("fieldset.field") || node.closest(".field");
  if (!wrapper) return;

  wrapper.classList.add("has-error");

  // aria-invalid on the input itself (or the fieldset, for radio groups)
  const ariaTarget = (wrapper.tagName === "FIELDSET") ? wrapper : node;
  ariaTarget.setAttribute("aria-invalid", "true");

  // inject a visible error message (the .field-error-msg CSS already exists)
  if (!wrapper.querySelector(".field-error-msg")) {
    const msg = document.createElement("p");
    msg.className = "field-error-msg";
    msg.textContent = "This one's required.";
    wrapper.appendChild(msg);
  }
}

function clearAllErrors() {
  form.querySelectorAll(".has-error").forEach(n => n.classList.remove("has-error"));
  form.querySelectorAll("[aria-invalid='true']").forEach(n => n.removeAttribute("aria-invalid"));
  form.querySelectorAll(".field-error-msg").forEach(n => n.remove());
  errorEl.hidden = true;
  errorEl.textContent = "";
}

function clearFieldError(ev) {
  const target = ev.target;
  if (!target?.name) return;
  const wrapper = target.closest("fieldset.field") || target.closest(".field");
  if (wrapper) {
    wrapper.classList.remove("has-error");
    const msg = wrapper.querySelector(".field-error-msg");
    if (msg) msg.remove();
    if (wrapper.tagName === "FIELDSET") wrapper.removeAttribute("aria-invalid");
  }
  target.removeAttribute("aria-invalid");
  if (!form.querySelectorAll(".has-error").length) {
    errorEl.hidden = true;
  }
}

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.hidden = false;
}

function scrollToFirstError() {
  const first = form.querySelector(".has-error");
  if (first) first.scrollIntoView({ behavior: "smooth", block: "center" });
}

/* ------------------------------ states ----------------------------------- */

function setSubmitting(yes) {
  submitBtn.disabled = yes;
  submitBtn.querySelector(".submit-label").textContent = yes ? "Sending…" : "Send my answers";
  // Hide the italic sub-line ("it goes only to me") while submitting so the
  // button reads cleanly as "Sending…" instead of "Sending… / it goes only to me."
  submitBtn.querySelector(".submit-sub").hidden = yes;
}

function showThanks(name) {
  document.getElementById("thanks-name").textContent =
    (name && name.split(/\s+/)[0]) || "friend";
  form.hidden = true;
  // Hide the intro paragraph too — once the response is in, the
  // "here's what this survey is for" framing isn't relevant anymore.
  const masthead = document.querySelector(".masthead");
  if (masthead) masthead.hidden = true;
  thanks.hidden = false;
  thanks.scrollIntoView({ behavior: "smooth", block: "start" });
}
