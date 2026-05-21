# Respondent-facing content audit

This is the complete inventory of everything a respondent can read or click. Scan it before sending the survey to anyone new — every link should resolve, every line of copy should reflect Jonathan's voice.

**Last verified:** 2026-05-21. URL status checked via `curl -L`. All resolve to 2xx unless noted.

To regenerate this doc after edits, ask Claude (or re-run the URL check at the bottom of this file).

---

## Outbound links

The survey is **read-only** for respondents — nothing they type leaves the form except via submit to Jon's private Google Sheet. The only outbound links are the resource cards in the post-submit panel. All 14 links below are surfaced AFTER submit, never before. Each opens in a new tab (`target="_blank" rel="noopener noreferrer"`).

### Setup section (always shown to every respondent)

Intro line shown above the cards:
> Two things I'd ask you to set up before we talk — they'll make our conversation much easier.


| Title | URL | Source | Summary |
|---|---|---|---|
| Sign up for Claude Pro | https://claude.com/pricing | Anthropic | Unlock the Claude 4 family and higher usage limits ($20/month). This is the version I'll be using when we talk. |
| Download the Claude desktop app | https://claude.com/download | Anthropic | The cleanest day-to-day experience — keyboard shortcuts, file uploads, a window separate from your browser tabs. Mac and Windows. |

### Curated resource library (top 4 shown, scored against respondent answers)

Intro line shown above the cards:
> Picked these based on what you said. **Not required reading before we meet** — just suggestions for your own curiosity, if you'd like to poke around. We'll cover what matters when we talk.


| Title | URL | Source | Summary |
|---|---|---|---|
| Getting started with Claude | https://platform.claude.com/docs/en/intro | Anthropic Docs | The official starting point — chat, projects, what the model is actually good at. |
| One Useful Thing | https://www.oneusefulthing.org/ | Ethan Mollick (Wharton) | Plain-English essays on actually using AI for work. The best ongoing source if you want to stay current without becoming an engineer. |
| Intro to large language models | https://www.youtube.com/watch?v=zjkBMFhNj_g | Andrej Karpathy · YouTube | A one-hour deep dive on how LLMs actually work, from one of the most respected engineers in the field. Watch if you want to understand the engine. |
| Anthropic's prompt engineering guide | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview | Anthropic Docs | Concrete techniques for writing prompts that get the answers you actually want. Skim the headings; read the bits that surprise you. |
| Simon Willison's weblog | https://simonwillison.net/ | simonwillison.net | Daily practical posts from one of the smartest independent observers of AI. Especially good once you start building. |
| What are Projects in Claude? | https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects | Anthropic Help | Projects let you collect documents and reuse instructions in one place — the simplest version of giving AI persistent context. |
| NotebookLM | https://notebooklm.google.com/ | Google | Drop a few PDFs in, get a Q&A interface trained on just those sources. The fastest way to feel what "AI on your own documents" can do. |
| Claude Code | https://claude.com/product/claude-code | Anthropic | An AI coding assistant that runs in your terminal — works alongside you on real codebases. The best entry point if you want to start building. |
| Cursor | https://www.cursor.com/ | cursor.com | An AI-native code editor. Less terminal-y than Claude Code, more visual. Try both and see which fits. |
| Anthropic API quickstart | https://platform.claude.com/docs/en/api/overview | Anthropic Docs | The five-minute path from "I have an idea" to "I have a working Python script that calls Claude." |
| The state of AI in 2025 | https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai | McKinsey | Where AI adoption actually is across industries, what's working, what isn't. Useful if you're trying to make sense of the noise for a team. |
| Privacy and Claude | https://privacy.claude.com/en/ | Anthropic | How Anthropic handles your data — retention, training, and what they do (and don't do) with conversations. Worth reading before pasting anything sensitive. |

### Footer (every page)

| Link | Destination |
|---|---|
| jon.sims@gmail.com | `mailto:` |

---

## Term popover definitions

Click an ⓘ icon next to a technical chip → modal opens with this text. Defined in `form.js → TERM_DEFINITIONS`.

| Term | Body text shown |
|---|---|
| AI agents | An AI that doesn't just answer — it does things. You give it a goal, it browses the web, edits files, sends emails, and so on. Still early but moving fast. |
| Connecting AI to your own documents | Sometimes called "RAG." The AI gets connected to YOUR documents or knowledge base so it can answer based on your stuff, not just what it learned during training. NotebookLM is one popular way in. |
| The API | The way developers connect their own software directly to Claude or ChatGPT. If you're not writing code, you can ignore this — but it's how custom integrations get built. |
| "Projects" and custom GPTs | Saved AI personas configured for a specific task — like a writing assistant pre-loaded with your style guide, or a research helper that already has your source documents attached. |
| Workflows and templates | Reusable prompt patterns or step-by-step processes you save once and run many times. Lets you stop re-explaining what you want each session. |
| Having AI write scripts for you | Instead of you writing code, you describe what you want and the AI writes the code. Sometimes called "vibe coding" — you direct, it implements. |
| Building little internal tools | Small applications — dashboards, forms, calculators — that solve specific problems for you or your team. Often built by describing them to AI instead of coding from scratch. |
| Connecting tools together via APIs | APIs are the channels by which software programs talk to each other. AI can help you bridge tools that don't natively integrate — e.g. "when a row is added to this sheet, send a Slack message and create a calendar event." |
| No-code tools | Tools like Zapier, Airtable, Notion, or Make.com that let you build workflows by clicking and connecting — no programming required. |

---

## Form copy — generic variant (`/`)

### Masthead intro
> Thanks for being open to a conversation about AI. This survey is here to help me understand where you are today — what you've tried, what you'd like to do, and where you'd like a hand. There are no wrong answers; the goal is to make our time together more useful.
>
> Nine short sections · about 3–4 minutes · your responses come only to me.

### Thank-you state (after submit)
> **Got it.**
>
> **Thanks, [first name].**
>
> I'll read through your answers and be in touch shortly. If anything else comes to mind in the meantime, drop me a note at jon.sims@gmail.com.
>
> — Jonathan Sims

### Footer
> Jonathan Sims · jon.sims@gmail.com · AI & technology consulting

### Submit button
> Send my answers
> *it goes only to me*

### Validation error messages
> "This one's required." (under each missing field)
> "Missing a few answers — see the highlighted questions above." (at submit-button level)
> "Couldn't send right now. Email me your answers instead, or try again in a minute." (network failure)

### Sending state
> Sending… (replaces submit button label)

---

## Form copy — Frank & Brittney variant (`/for-frank-and-brittney/`)

Only the masthead, thank-you, and footer differ from the generic. Everything else is shared.

### Masthead intro
> Frank, Brittney — thanks for letting me try this with you. I've put a short survey together to map where you each are with AI today and where you'd like to go. Each of you fills it out on your own — there are no wrong answers; the goal is to make our time together more useful.
>
> Nine short sections · about 3–4 minutes · your responses come only to me.

### Thank-you state (after submit)
> **Got it.**
>
> **Thanks, [first name].**
>
> I'll read through and we'll talk soon. Anything else, just text me.
>
> — Jon

### Footer
> Jonathan Sims · jon.sims@gmail.com

---

## Question copy — all variants

Every label, every option, every help line. Top to bottom of the form.

### 1. Hello
- Card intro: *Let's start easy.*
- Your name (required)
- What you do / your role — placeholder: *e.g. founder, teacher, ops lead…*

### 2. How familiar are you with AI today?
- Card intro: *Two quick takes — a scale and a checklist.*
- **Scale (required):** Pick the description that fits best right now.
  1. I've heard of ChatGPT.
  2. I've used it once or twice.
  3. I use it occasionally for specific tasks.
  4. I use it daily and have opinions about which tools are best.
  5. I build with AI — prompts, agents, APIs, custom workflows.
- **Chips:** Which of these have you tried or heard of? · Pick any that apply.
  - prompting / chatting
  - image generation
  - voice & transcription
  - "Projects" or custom GPTs
  - agents that do tasks for you
  - connecting AI to your own documents
  - writing code with AI
  - the API

### 3. Tools you've used
- Card intro: *A quick map of what you've touched.*
- **Chips:** ChatGPT · Claude (Anthropic) · Gemini (Google) · Copilot (Microsoft 365) · GitHub Copilot · Perplexity · Midjourney / DALL·E · NotebookLM · Cursor · other
- **Free text:** If you've used Claude, what stood out? · *Good, bad, or surprising — one thing is fine.*
- **Free text:** Where have these tools fallen short for you?

### 4. What do you want to do with AI?
- **Chips:** write & communicate better · analyze data / make sense of information · automate repetitive work · build something (apps, tools) · talk about it intelligently with colleagues · just curious / exploring · other
- **Free text:** Describe one specific situation where you've thought "AI should help with this." · *A real moment from your work is more useful than an abstract example.*

### 5. What's the data situation?
- Card intro: *This shapes which tools and approaches I'd recommend — some are fine for everyday work, others matter once regulated or sensitive data is in the mix.*
- **Chips:** Does the work you'd want AI to help with involve any of these? · *Pick what applies. If you're not sure, leave it.*
  - client or customer personal info
  - health or medical data
  - financial or banking data
  - student or education records
  - legal documents
  - proprietary IP or trade secrets
  - materials under NDA
  - nothing especially sensitive

### 6. Your toolkit today
- Card intro: *A quick look at what you already work with.*
- **Scale (required):** 1–5 from "Spreadsheets are my limit." to "I write code."
- **Chips:** What do you actually do with computers, on a regular week? · email & documents · spreadsheets with formulas · no-code tools (Zapier, Notion, Airtable) · light scripting · real coding
- **Chips:** Specialized software you've worked with at the office. · *Even briefly, even years ago. Pick what fits.* · Excel power tools / Tableau-Power BI-Looker / SQL / statistical software / Python or R / CRM / ERP / project management / design tools / accounting
- **Free text:** Anything industry-specific or specialized I should know you've used?

### 7. What you'd want to learn
- Card intro: *If you had a guide, what would you reach for?*
- **Radio stack:** How do you feel about the technical side of AI?
  - Not for me — just give me what works.
  - I'll learn what I have to, no more.
  - Open to learning, when it's clearly useful.
  - Curious — I want to dig in.
  - I want to build things myself.
- **Chips:** Which of these would you be open to learning? · *Pick the ones you're curious about, even tentatively.* · writing better prompts / building reusable workflows / using AI to clean up and analyze your own data / having AI write small scripts / building little internal tools / connecting tools via APIs / training AI on your own documents / none of the above, honestly

### 8. Where could things be better?
- Card intro: *The honest stuff. These two answers shape the whole conversation.*
- **Free text:** Where do you waste time, or feel stuck, in your work?
- **Free text:** If we do good work together, what's different in your week six months from now? · *Concrete is better than visionary. A morning meeting that's faster, an hour back on Fridays, a report you stop dreading.*

### 9. Anything else I should know?
- Card intro: *Optional. Anything you want to flag before we talk.*
- Placeholder: *Could be a question, a worry, a wild idea…*

---

## What does NOT get shared with respondents

For belt-and-suspenders clarity, here's what respondents NEVER see:

- Other respondents' submissions
- The list of which client-variants exist
- The Apps Script URL or Sheet ID
- Any analytics or telemetry (the form has none)
- Cookies (none set)
- Third-party scripts (none — only Google Fonts CSS is loaded externally)

---

## Outstanding notes

- **McKinsey URL:** their WAF blocks `curl` requests (status 000 from scripts), but the page resolves cleanly in a browser. Manual spot-check recommended periodically.
- **Anthropic rebrand:** Anthropic is consolidating documentation under `claude.com` (away from `anthropic.com` / `docs.anthropic.com`). All redirects work, but we've updated to the canonical destinations to skip the hop. Re-verify quarterly.
- **NotebookLM:** redirects to Google sign-in for unauthenticated visitors — expected behavior; the destination is correct.
- **YouTube link** (Karpathy): video could in theory be removed by the uploader. Spot-check periodically.

---

## How to regenerate this audit

When the resource library, term definitions, or any user-facing copy changes in `form.js` or `index.html`, this file should be updated. Ask Claude in a session: *"regenerate the AUDIT.md from current source files."*
