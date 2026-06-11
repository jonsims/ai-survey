# TODO — Frank and Brittney AI

## Done (this session)
- [x] Research public databases for MHP/affordable housing expansion analysis
- [x] Download and catalog 5 federal datasets (LIHTC, FMR, Income Limits, QCT/DDA, IRS Migration)
- [x] Write datasets/README.md with column dictionary and suggested joins
- [x] Write PRD for analytics demo (privacy-sanitized)
- [x] Phase 1: first analytics story (migration vs LIHTC supply) — end to end
- [x] Phase 2: three more stories (rent burden, subsidy expirations, FMR trajectory)
- [x] Static HTML dashboard (build.py → for-frank-and-brittney/demo/)
- [x] Interactive Marimo dashboard with sliders and Folium map (port 2718)
- [x] Emma's Estates design reference deployed
- [x] v1 unified dashboard: Emma's Estates aesthetic + real data + Plotly charts + rent simulation
- [x] 6-agent design review (graphic designer, UX, owner, accountant, consultant, RE software)
- [x] v2 redesign: rent-planner-first, data-dense work tool, simplified tables + detail modal
- [x] 50-property dummy portfolio with AMI ceilings and expense breakdowns
- [x] Prestige Worldwide branding + easter egg
- [x] Rent Decision tab: per-property waterfall chart + expense modeling + slider projections
- [x] Codex code review: fixed AMI ceiling cap-down bug, waterfall chart, truthiness checks
- [x] 12-term glossary with auto-wrapping click-to-define tooltips
- [x] 8-step how-to guide with clickable tab links and contextual banners
- [x] 3-agent guide review: reordered steps, rewrote intro, added lease timing
- [x] Properties grid view with type-specific SVG illustrations
- [x] Multiple UX passes: font sizing, column spacing, modal readability

## Next
- [ ] Connect to real client data (replace dummy portfolio CSV)
- [ ] Add lease expiration dates to property data for notice scheduling
- [ ] Per-property expense editing (currently uses portfolio-wide assumptions)
- [ ] Scenario save/compare (name 2-3 scenarios, view side by side)
- [ ] Print-friendly / PDF export of the rent plan
- [ ] Consider backend (SQLite + Flask) if multi-user or audit trail needed
- [ ] LIHTC compliance audit trail: datestamped rent-setting records
