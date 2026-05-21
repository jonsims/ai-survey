/*  AI Intake Survey — form.js
    Shared across the generic form and all per-client variants.
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

/* ------------------------- term popovers ----------------------------- */
/* Plain-English definitions for the technical terms that appear in chip
   labels. JS injects a tiny "ⓘ" button into chips whose value is in the
   map; clicking it opens a modal. No HTML changes needed in any variant. */

const TERM_DEFINITIONS = {
  agents: {
    title: "AI agents",
    body: "An AI that doesn't just answer — it does things. You give it a goal, it browses the web, edits files, sends emails, and so on. Still early but moving fast."
  },
  rag: {
    title: "Connecting AI to your own documents",
    body: "Sometimes called \"RAG.\" The AI gets connected to YOUR documents or knowledge base so it can answer based on your stuff, not just what it learned during training. NotebookLM is one popular way in."
  },
  api: {
    title: "The API",
    body: "The way developers connect their own software directly to Claude or ChatGPT. If you're not writing code, you can ignore this — but it's how custom integrations get built."
  },
  custom_gpts: {
    title: "\"Projects\" and custom GPTs",
    body: "Saved AI personas configured for a specific task — like a writing assistant pre-loaded with your style guide, or a research helper that already has your source documents attached."
  },
  workflows: {
    title: "Workflows and templates",
    body: "Reusable prompt patterns or step-by-step processes you save once and run many times. Lets you stop re-explaining what you want each session."
  },
  scripts: {
    title: "Having AI write scripts for you",
    body: "Instead of you writing code, you describe what you want and the AI writes the code. Sometimes called \"vibe coding\" — you direct, it implements."
  },
  little_tools: {
    title: "Building little internal tools",
    body: "Small applications — dashboards, forms, calculators — that solve specific problems for you or your team. Often built by describing them to AI instead of coding from scratch."
  },
  apis_learning: {
    title: "Connecting tools together via APIs",
    body: "APIs are the channels by which software programs talk to each other. AI can help you bridge tools that don't natively integrate — e.g. \"when a row is added to this sheet, send a Slack message and create a calendar event.\""
  },
  no_code: {
    title: "No-code tools",
    body: "Tools like Zapier, Airtable, Notion, or Make.com that let you build workflows by clicking and connecting — no programming required."
  }
};

/* Which (field-name, value) pairs should get an info button injected,
   and which term to show. Same value can map to different terms in
   different sections (e.g. ai_concepts_known.api vs learning_openness.apis). */
const CHIP_TERM_MAP = {
  "ai_concepts_known:agents":      "agents",
  "ai_concepts_known:rag":         "rag",
  "ai_concepts_known:api":         "api",
  "ai_concepts_known:custom_gpts": "custom_gpts",
  "tech_activities:no_code":       "no_code",
  "learning_openness:workflows":    "workflows",
  "learning_openness:scripts":      "scripts",
  "learning_openness:little_tools": "little_tools",
  "learning_openness:apis":         "apis_learning",
  "learning_openness:own_data":     "rag",
  "learning_openness:own_knowledge":"rag",
};

/* -------------------------- starter resources ------------------------ */
/* Two-tier post-submit panel:
   • SETUP_ITEMS shows for everyone — the "get set up" calls to action
   • RESOURCES is the curated library, scored against the respondent's
     answers; top N matches are shown as a personalized reading list. */

const SETUP_ITEMS = [
  {
    title: "Sign up for Claude Pro",
    source: "Anthropic",
    type: "signup",
    url: "https://claude.com/pricing",
    summary: "Unlock the Claude 4 family and higher usage limits ($20/month). This is the version I'll be using when we talk."
  },
  {
    title: "Download the Claude desktop app",
    source: "Anthropic",
    type: "download",
    url: "https://claude.com/download",
    summary: "The cleanest day-to-day experience — keyboard shortcuts, file uploads, a window separate from your browser tabs. Mac and Windows."
  }
];

const RESOURCES = [
  {
    title: "Getting started with Claude",
    source: "Anthropic Docs",
    type: "docs",
    url: "https://platform.claude.com/docs/en/intro",
    summary: "The official starting point — chat, projects, what the model is actually good at.",
    level: [1, 2, 3], tech: [1, 2, 3, 4, 5],
    goals: ["curious", "write", "converse"],
    topics: ["prompting"]
  },
  {
    title: "One Useful Thing",
    source: "Ethan Mollick (Wharton)",
    type: "newsletter",
    url: "https://www.oneusefulthing.org/",
    summary: "Plain-English essays on actually using AI for work. The best ongoing source if you want to stay current without becoming an engineer.",
    level: [1, 2, 3, 4], tech: [1, 2, 3, 4, 5],
    goals: ["write", "analyze", "automate", "converse", "curious"],
    topics: ["prompting", "workflows", "own_data"]
  },
  {
    title: "Intro to large language models",
    source: "Andrej Karpathy · YouTube",
    type: "video",
    url: "https://www.youtube.com/watch?v=zjkBMFhNj_g",
    summary: "A one-hour deep dive on how LLMs actually work, from one of the most respected engineers in the field. Watch if you want to understand the engine.",
    level: [2, 3, 4, 5], tech: [2, 3, 4, 5],
    goals: ["curious", "build"],
    topics: ["prompting", "scripts", "apis"]
  },
  {
    title: "Anthropic's prompt engineering guide",
    source: "Anthropic Docs",
    type: "docs",
    url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview",
    summary: "Concrete techniques for writing prompts that get the answers you actually want. Skim the headings; read the bits that surprise you.",
    level: [2, 3, 4, 5], tech: [1, 2, 3, 4, 5],
    goals: ["write", "analyze", "automate", "build"],
    topics: ["prompting"]
  },
  {
    title: "Simon Willison's weblog",
    source: "simonwillison.net",
    type: "blog",
    url: "https://simonwillison.net/",
    summary: "Daily practical posts from one of the smartest independent observers of AI. Especially good once you start building.",
    level: [3, 4, 5], tech: [3, 4, 5],
    goals: ["build", "curious"],
    topics: ["prompting", "apis", "little_tools", "scripts", "own_knowledge"]
  },
  {
    title: "What are Projects in Claude?",
    source: "Anthropic Help",
    type: "docs",
    url: "https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects",
    summary: "Projects let you collect documents and reuse instructions in one place — the simplest version of giving AI persistent context.",
    level: [2, 3, 4], tech: [1, 2, 3],
    goals: ["write", "analyze", "automate"],
    topics: ["workflows", "own_knowledge"]
  },
  {
    title: "NotebookLM",
    source: "Google",
    type: "tool",
    url: "https://notebooklm.google.com/",
    summary: "Drop a few PDFs in, get a Q&A interface trained on just those sources. The fastest way to feel what \"AI on your own documents\" can do.",
    level: [1, 2, 3, 4], tech: [1, 2, 3, 4, 5],
    goals: ["analyze", "write"],
    topics: ["own_data", "own_knowledge"]
  },
  {
    title: "Claude Code",
    source: "Anthropic",
    type: "tool",
    url: "https://claude.com/product/claude-code",
    summary: "An AI coding assistant that runs in your terminal — works alongside you on real codebases. The best entry point if you want to start building.",
    level: [4, 5], tech: [3, 4, 5],
    goals: ["build", "automate"],
    topics: ["scripts", "little_tools", "apis"]
  },
  {
    title: "Cursor",
    source: "cursor.com",
    type: "tool",
    url: "https://www.cursor.com/",
    summary: "An AI-native code editor. Less terminal-y than Claude Code, more visual. Try both and see which fits.",
    level: [3, 4, 5], tech: [3, 4, 5],
    goals: ["build"],
    topics: ["scripts", "little_tools"]
  },
  {
    title: "Anthropic API quickstart",
    source: "Anthropic Docs",
    type: "docs",
    url: "https://platform.claude.com/docs/en/api/overview",
    summary: "The five-minute path from \"I have an idea\" to \"I have a working Python script that calls Claude.\"",
    level: [4, 5], tech: [4, 5],
    goals: ["build"],
    topics: ["apis", "scripts"]
  },
  {
    title: "The state of AI in 2025",
    source: "McKinsey",
    type: "report",
    url: "https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai",
    summary: "Where AI adoption actually is across industries, what's working, what isn't. Useful if you're trying to make sense of the noise for a team.",
    level: [1, 2, 3, 4], tech: [1, 2, 3, 4, 5],
    goals: ["converse", "curious"],
    topics: ["workflows"]
  },
  {
    title: "Privacy and Claude",
    source: "Anthropic",
    type: "docs",
    url: "https://privacy.claude.com/en/",
    summary: "How Anthropic handles your data — retention, training, and what they do (and don't do) with conversations. Worth reading before pasting anything sensitive.",
    level: [1, 2, 3, 4, 5], tech: [1, 2, 3, 4, 5],
    goals: [], topics: [],
    privacy: true   // boosted when respondent flagged regulated/sensitive data
  }
];

/* ------------------------------- DOM refs --------------------------------- */

const form    = document.getElementById("survey");
const thanks  = document.getElementById("thanks");
const errorEl = form.querySelector(".submit-error");
const submitBtn = form.querySelector(".submit-btn");

form.addEventListener("submit", onSubmit);
form.addEventListener("input",  clearFieldError);
form.addEventListener("change", clearFieldError);

/* Adaptive: re-evaluate which chips to hide whenever a trigger field
   changes (familiarity scale, tech comfort scale, curiosity radio stack). */
form.addEventListener("change", applyAdaptiveRules);

/* Term popovers — capture-phase document listener so the click is handled
   BEFORE bubbling to the chip's <label>, preventing the chip from toggling
   when the user just wanted a definition. */
document.addEventListener("click", onDocumentClick, true);
document.addEventListener("keydown", onDocumentKey);

/* On load, walk the chips and inject info buttons next to the technical
   ones, and seed the adaptive state from any existing selections. */
injectTermInfoButtons();
applyAdaptiveRules();

/* -------------------------------- submit ---------------------------------- */

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
    .then(() => showThanks(data))
    .catch((err) => {
      console.error("[ai-survey] submit failed:", err);
      showError("Couldn't send right now. Email me your answers instead, or try again in a minute.");
      setSubmitting(false);
    });
}

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
  MULTI_SELECTS.forEach(k => { if (!(k in out)) out[k] = []; });

  out.client = formEl.dataset.client || "generic";

  return out;
}

function isEmpty(v) {
  if (Array.isArray(v)) return v.length === 0;
  return v == null || String(v).trim() === "";
}

function send(data) {
  const body = JSON.stringify(data);

  if (!APPS_SCRIPT_URL) {
    console.log("[ai-survey] payload (no APPS_SCRIPT_URL set):", data);
    return new Promise(r => setTimeout(r, 400));
  }

  return fetch(APPS_SCRIPT_URL, {
    method: "POST",
    mode: "no-cors",
    headers: { "Content-Type": "text/plain;charset=utf-8" },
    body,
  });
}

/* ------------------------------ errors ----------------------------------- */

function markFieldError(name) {
  const node = form.querySelector(`[name="${name}"]`);
  if (!node) return;
  const wrapper = node.closest("fieldset.field") || node.closest(".field");
  if (!wrapper) return;

  wrapper.classList.add("has-error");
  const ariaTarget = (wrapper.tagName === "FIELDSET") ? wrapper : node;
  ariaTarget.setAttribute("aria-invalid", "true");

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
  submitBtn.querySelector(".submit-sub").hidden = yes;
}

function showThanks(data) {
  document.getElementById("thanks-name").textContent =
    (data.name && data.name.split(/\s+/)[0]) || "friend";
  form.hidden = true;
  const masthead = document.querySelector(".masthead");
  if (masthead) masthead.hidden = true;

  renderResources(data);

  thanks.hidden = false;
  thanks.scrollIntoView({ behavior: "smooth", block: "start" });
}

/* ----------------------- adaptive question hiding ------------------------ */
/* Three rules:
   1. tech_curiosity in {not_for_me, reluctant} → hide the coding-heavy
      learning chips (scripts, little_tools, apis)
   2. tech_comfort = 1 → hide deeply-technical specialized_software chips
      (sql, python_r, stats, erp) and the technical concept chips
      (api, rag, agents) in ai_concepts_known
   3. ai_familiarity = 1 → hide the same technical concept chips even if
      tech_comfort is higher (still very new to AI vocabulary)
   Hidden chips also get their checkbox unchecked so a re-shown chip's
   prior value doesn't silently submit. */

function applyAdaptiveRules() {
  const curiosity   = form.querySelector("[name=tech_curiosity]:checked")?.value || "";
  const techComfort = form.querySelector("[name=tech_comfort]:checked")?.value   || "";
  const aiFam       = form.querySelector("[name=ai_familiarity]:checked")?.value || "";

  form.dataset.curiosity      = curiosity;
  form.dataset.techComfort    = techComfort;
  form.dataset.aiFamiliarity  = aiFam;

  // Uncheck anything that's now hidden so it doesn't ride along in submit
  requestAnimationFrame(() => {
    form.querySelectorAll(".chip").forEach(chip => {
      const cs = getComputedStyle(chip);
      if (cs.display === "none") {
        const input = chip.querySelector("input[type=checkbox]");
        if (input?.checked) input.checked = false;
      }
    });
  });
}

/* ---------------------------- term popovers ------------------------------ */

function injectTermInfoButtons() {
  form.querySelectorAll(".chip input[type=checkbox]").forEach(input => {
    const key = `${input.name}:${input.value}`;
    const term = CHIP_TERM_MAP[key];
    if (!term) return;

    const chip = input.closest(".chip");
    if (chip.querySelector(".term-info")) return;

    const btn = document.createElement("span");
    btn.className = "term-info";
    btn.dataset.term = term;
    btn.setAttribute("role", "button");
    btn.setAttribute("tabindex", "0");
    btn.setAttribute("aria-label", "What does this mean?");
    btn.textContent = "ⓘ";
    chip.appendChild(btn);
  });
}

function onDocumentClick(ev) {
  // Term-info click → open modal (capture phase, so we beat the <label>)
  const info = ev.target.closest && ev.target.closest(".term-info");
  if (info) {
    ev.preventDefault();
    ev.stopPropagation();
    openTermModal(info.dataset.term);
    return;
  }
  // Modal close affordances: the close button or the overlay backdrop
  if (ev.target.matches?.(".term-modal-close, .term-modal-overlay")) {
    closeTermModal();
  }
}

function onDocumentKey(ev) {
  // Enter/Space on a focused term-info → open modal
  if ((ev.key === "Enter" || ev.key === " ") && ev.target.matches?.(".term-info")) {
    ev.preventDefault();
    openTermModal(ev.target.dataset.term);
    return;
  }
  // Escape → close modal
  if (ev.key === "Escape") closeTermModal();
}

function openTermModal(term) {
  const def = TERM_DEFINITIONS[term];
  if (!def) return;

  let modal = document.getElementById("term-modal");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "term-modal";
    modal.className = "term-modal";
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.innerHTML = `
      <div class="term-modal-overlay"></div>
      <div class="term-modal-card">
        <h3 class="term-modal-title"></h3>
        <p class="term-modal-body"></p>
        <button type="button" class="term-modal-close">close</button>
      </div>
    `;
    document.body.appendChild(modal);
  }
  modal.querySelector(".term-modal-title").textContent = def.title;
  modal.querySelector(".term-modal-body").textContent = def.body;
  modal.hidden = false;
  // Focus the close button so Escape/Enter work immediately
  modal.querySelector(".term-modal-close").focus();
}

function closeTermModal() {
  const modal = document.getElementById("term-modal");
  if (modal) modal.hidden = true;
}

/* ------------------------- resource matching ----------------------------- */

function scoreResource(r, data) {
  const fam  = parseInt(data.ai_familiarity, 10);
  const tech = parseInt(data.tech_comfort, 10);

  // Drop resources outside the familiarity/tech range
  if (r.level && !r.level.includes(fam))  return 0;
  if (r.tech  && !r.tech.includes(tech))  return 0;

  let score = 1; // base score for landing in range

  // Boost for goal overlap (each matched goal is worth more than topic match)
  const goals = data.goals || [];
  const goalsOverlap = (r.goals || []).filter(g => goals.includes(g)).length;
  score += goalsOverlap * 2;

  // Boost for learning_openness (topics) overlap
  const topics = data.learning_openness || [];
  const topicsOverlap = (r.topics || []).filter(t => topics.includes(t)).length;
  score += topicsOverlap * 1.5;

  // Strong boost for the privacy resource if they flagged any sensitive data
  const regulated = data.regulated_data || [];
  const hasSensitive = regulated.some(d => d !== "nothing_sensitive");
  if (r.privacy && hasSensitive) score += 6;

  return score;
}

function pickResources(data, n = 4) {
  return RESOURCES
    .map(r => ({ ...r, _score: scoreResource(r, data) }))
    .filter(r => r._score > 0)
    .sort((a, b) => b._score - a._score)
    .slice(0, n);
}

/* ------------------------- resource rendering ---------------------------- */

function renderResources(data) {
  // Skip rendering if we somehow lack the required fields (shouldn't happen
  // because submit is gated on the two scales, but be defensive).
  if (!data.ai_familiarity || !data.tech_comfort) return;

  const picks = pickResources(data, 4);

  // Build the panel
  const panel = document.createElement("div");
  panel.className = "resources";
  panel.innerHTML = `
    <div class="resources-block">
      <p class="kicker">Get set up</p>
      <p class="resources-intro">Two things I'd ask you to set up before we talk — they'll make our conversation much easier.</p>
      <ul class="resource-list">
        ${SETUP_ITEMS.map(renderResourceItem).join("")}
      </ul>
    </div>
    ${picks.length ? `
      <div class="resources-block">
        <p class="kicker">A few things to read or watch</p>
        <p class="resources-intro">Picked these based on what you said. <strong>Not required reading before we meet</strong> &mdash; just suggestions for your own curiosity, if you'd like to poke around. We'll cover what matters when we talk.</p>
        <ul class="resource-list">
          ${picks.map(renderResourceItem).join("")}
        </ul>
      </div>
    ` : ""}
  `;
  thanks.appendChild(panel);
}

function renderResourceItem(r) {
  const safe = (s) => String(s).replace(/[&<>"]/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]
  );
  return `
    <li class="resource-card">
      <a class="resource-title" href="${safe(r.url)}" target="_blank" rel="noopener noreferrer">${safe(r.title)}</a>
      <p class="resource-meta">${safe(r.source)} · ${safe(r.type)}</p>
      <p class="resource-summary">${safe(r.summary)}</p>
    </li>
  `;
}
