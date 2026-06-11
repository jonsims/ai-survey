"""Build v3: simplified tables + detail modal, 50 properties."""

import json
from pathlib import Path
from datetime import date

DATA_PATH = Path(__file__).resolve().parent / "output" / "v2_data.json"
OUT_PATH = Path(__file__).resolve().parent.parent / "for-frank-and-brittney" / "demo" / "v2" / "index.html"


def main():
    data = json.loads(DATA_PATH.read_text())
    s = data["summary"]
    today = date.today()

    # Planner rows — simplified: Name, Type, Units, Current Rent, Increase%, Proposed
    planner_rows = ""
    for p in data["properties"]:
        planner_rows += f"""<tr data-type="{p['type']}" data-state="{p['state']}" data-id="{p['id']}"
          data-rent="{p['current_rent']}" data-units="{p['units']}" data-occupied="{p['occupied']}"
          data-noi="{p['noi']}" data-opex="{p['expenses']['total']}" data-ds="{p['debt_service']}"
          data-ceiling="{p['ami_ceiling_rent'] or 99999}" data-restricted="{1 if p['rent_restricted'] else 0}"
          data-acq="{p['acquisition_price']}" data-fmr="{p['fmr_2br']}"
          data-ami-pct="{p['ami_ceiling_pct'] or ''}" data-ami-rent="{p['ami_ceiling_rent'] or ''}"
          data-headroom="{p['headroom_pct'] if p['headroom_pct'] is not None else ''}"
          data-occ="{p['occupancy_pct']}" data-county="{p['county']}"
          data-ins="{p['expenses']['insurance']}" data-tax="{p['expenses']['taxes']}"
          data-maint="{p['expenses']['maintenance']}" data-mgmt="{p['expenses']['management']}"
          data-cashflow="{p['cash_flow']}" data-coc="{p['cash_on_cash'] or ''}"
          data-dscr="{p['dscr'] or ''}" data-yearacq="{p['year_acquired']}"
          onclick="openModal(this)">
          <td class="c-name"><b>{p['name']}</b><span>{p['county']}, {p['state']}</span></td>
          <td><span class="pill pill-{p['type']}">{p['type_label']}</span></td>
          <td class="c-num">{p['units']}</td>
          <td class="c-money">${p['current_rent']:,.0f}</td>
          <td class="c-edit" onclick="event.stopPropagation()"><input type="number" class="inc-input" value="3" min="-10" max="30" step="0.5"/></td>
          <td class="c-money c-proposed">—</td>
        </tr>"""

    # Properties rows — simplified: Name, Type, Units, Rent, NOI
    prop_rows = ""
    for p in data["properties"]:
        prop_rows += f"""<tr data-type="{p['type']}" data-state="{p['state']}"
          data-id="{p['id']}" data-rent="{p['current_rent']}" data-units="{p['units']}" data-occupied="{p['occupied']}"
          data-noi="{p['noi']}" data-opex="{p['expenses']['total']}" data-ds="{p['debt_service']}"
          data-ceiling="{p['ami_ceiling_rent'] or 99999}" data-restricted="{1 if p['rent_restricted'] else 0}"
          data-acq="{p['acquisition_price']}" data-fmr="{p['fmr_2br']}"
          data-ami-pct="{p['ami_ceiling_pct'] or ''}" data-ami-rent="{p['ami_ceiling_rent'] or ''}"
          data-headroom="{p['headroom_pct'] if p['headroom_pct'] is not None else ''}"
          data-occ="{p['occupancy_pct']}" data-county="{p['county']}"
          data-ins="{p['expenses']['insurance']}" data-tax="{p['expenses']['taxes']}"
          data-maint="{p['expenses']['maintenance']}" data-mgmt="{p['expenses']['management']}"
          data-cashflow="{p['cash_flow']}" data-coc="{p['cash_on_cash'] or ''}"
          data-dscr="{p['dscr'] or ''}" data-yearacq="{p['year_acquired']}"
          onclick="openModal(this)">
          <td class="c-name"><b>{p['name']}</b><span>{p['county']}, {p['state']}</span></td>
          <td><span class="pill pill-{p['type']}">{p['type_label']}</span></td>
          <td class="c-num">{p['units']}</td>
          <td class="c-money">${p['current_rent']:,.0f}</td>
          <td class="c-money">${p['noi']:,.0f}</td>
        </tr>"""

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Portfolio Manager</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root {{
  --accent:#1F4A3D;--accent-light:#E6EDE9;--brass:#B07A2A;--brass-light:#F1E6D0;
  --slate:#3F4F75;--red:#C53030;--red-light:#FED7D7;--green:#276749;--green-light:#C6F6D5;
  --ink:#1A202C;--text:#2D3748;--muted:#718096;--border:#E2E8F0;--border-light:#EDF2F7;
  --bg:#F7FAFC;--card:#FFFFFF;
  --sans:"IBM Plex Sans","Helvetica Neue",Arial,sans-serif;
  --mono:"IBM Plex Mono","SF Mono",Menlo,monospace;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{height:100vh;overflow:hidden;background:var(--bg);color:var(--text);font-family:var(--sans);font-size:15px;line-height:1.4}}
body{{display:flex;flex-direction:column}}

.topbar{{flex:0 0 auto;display:flex;align-items:center;justify-content:space-between;padding:6px 16px;background:var(--card);border-bottom:1px solid var(--border);gap:12px}}
.brand{{font-weight:600;font-size:1.05rem;color:var(--accent);display:flex;align-items:center;gap:8px}}
.brand svg{{width:22px;height:22px}}
.tabs{{display:flex;gap:2px}}
.tab{{appearance:none;border:0;background:transparent;font-family:var(--sans);font-size:0.93rem;font-weight:500;color:var(--muted);padding:7px 14px;border-radius:6px;cursor:pointer}}
.tab:hover{{background:var(--bg);color:var(--text)}}
.tab.is-active{{background:var(--accent);color:#fff}}
.tab-badge{{font-family:var(--mono);font-size:0.75rem;background:rgba(255,255,255,.25);padding:1px 6px;border-radius:8px;margin-left:4px}}
.topbar-right{{display:flex;gap:8px;align-items:center}}
.btn{{appearance:none;border:1px solid var(--border);background:var(--card);font-family:var(--sans);font-size:0.9rem;font-weight:500;padding:6px 14px;border-radius:5px;cursor:pointer;color:var(--text)}}
.btn:hover{{border-color:var(--accent);color:var(--accent)}}
.btn-primary{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.btn-primary:hover{{background:#143A2E}}

.page{{flex:1;min-height:0;position:relative}}
.view{{display:none;height:100%;flex-direction:column;padding:8px 14px;gap:8px;overflow-y:auto}}
.view.is-active{{display:flex}}
.page-head{{flex:0 0 auto;display:flex;justify-content:space-between;align-items:flex-end;gap:16px}}
.page-head h1{{font-size:1.25rem;font-weight:600;color:var(--ink)}}
.page-head .sub{{font-size:0.88rem;color:var(--muted);margin-top:1px}}

.kpi-strip{{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;flex:0 0 auto}}
.kpi{{background:var(--card);border:1px solid var(--border);border-radius:6px;padding:8px 12px}}
.kpi-label{{font-size:0.78rem;font-weight:500;color:var(--muted);text-transform:uppercase;letter-spacing:0.05em}}
.kpi-val{{font-family:var(--mono);font-size:1.5rem;font-weight:600;color:var(--ink);margin:2px 0 1px}}
.kpi-note{{font-size:0.8rem;color:var(--muted)}}
.kpi-note.up{{color:var(--green)}}.kpi-note.down{{color:var(--red)}}

.bulk-bar{{display:flex;gap:8px;align-items:center;flex:0 0 auto;padding:6px 10px;background:var(--card);border:1px solid var(--border);border-radius:6px;flex-wrap:wrap}}
.bulk-bar label{{font-size:0.88rem;font-weight:500;color:var(--text)}}
.bulk-bar select,.bulk-bar input[type="number"]{{font-family:var(--mono);font-size:0.9rem;padding:4px 8px;border:1px solid var(--border);border-radius:4px;background:var(--card)}}
.bulk-bar input[type="number"]{{width:70px}}

.table-wrap{{flex:1;min-height:0;overflow:auto;background:var(--card);border:1px solid var(--border);border-radius:6px}}
table{{width:100%;border-collapse:collapse;font-size:0.93rem}}
thead th{{position:sticky;top:0;background:var(--bg);border-bottom:2px solid var(--border);padding:6px 10px;text-align:left;font-weight:600;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.04em;color:var(--muted);white-space:nowrap;z-index:2}}
tbody td{{padding:6px 10px;border-bottom:1px solid var(--border-light);vertical-align:middle}}
tbody tr{{cursor:pointer}}
tbody tr:hover{{background:var(--accent-light)}}
.c-name b{{display:block;font-weight:500;color:var(--ink)}}
.c-name span{{display:block;font-size:0.82rem;color:var(--muted)}}
.c-num{{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums}}
.c-money{{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums}}
.c-edit{{text-align:center}}
.inc-input{{width:62px;font-family:var(--mono);font-size:0.95rem;padding:3px 6px;border:1px solid var(--border);border-radius:4px;text-align:right;background:var(--card)}}
.inc-input:focus{{outline:2px solid var(--accent);border-color:var(--accent)}}
.pill{{display:inline-block;font-size:0.8rem;font-weight:500;padding:2px 8px;border-radius:10px}}
.pill-mhp_lot{{background:var(--accent-light);color:var(--accent)}}
.pill-lihtc_apartment{{background:var(--brass-light);color:var(--brass)}}
.pill-market_apartment{{background:#E2E8F0;color:var(--slate)}}
tr.at-ceiling td{{background:var(--red-light)}}
tr.at-ceiling .c-proposed{{color:var(--red);font-weight:600}}

.filter-bar{{display:flex;gap:8px;align-items:center;flex:0 0 auto}}
.filter-bar select{{font-size:0.9rem;padding:5px 8px;border:1px solid var(--border);border-radius:5px}}

.chart-row{{display:grid;grid-template-columns:1fr 1fr;gap:8px;flex:0 0 auto}}
.chart-panel{{background:var(--card);border:1px solid var(--border);border-radius:6px;padding:10px}}
.chart-panel h3{{font-size:0.92rem;font-weight:600;margin-bottom:6px}}

/* ── Modal ── */
.modal-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:100;align-items:center;justify-content:center}}
.modal-overlay.open{{display:flex}}
.modal{{background:var(--card);border-radius:10px;box-shadow:0 20px 60px rgba(0,0,0,.2);width:560px;max-height:85vh;overflow-y:auto;padding:0}}
.modal-header{{display:flex;justify-content:space-between;align-items:flex-start;padding:16px 20px 12px;border-bottom:1px solid var(--border)}}
.modal-header h2{{font-size:1.15rem;font-weight:600;color:var(--ink)}}
.modal-header .modal-sub{{font-size:0.85rem;color:var(--muted);margin-top:2px}}
.modal-close{{appearance:none;border:0;background:transparent;font-size:1.4rem;color:var(--muted);cursor:pointer;padding:0 4px;line-height:1}}
.modal-close:hover{{color:var(--ink)}}
.modal-body{{padding:16px 20px}}
.detail-grid{{display:grid;grid-template-columns:1fr 1fr;gap:2px 16px}}
.detail-row{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border-light)}}
.detail-row:last-child{{border-bottom:0}}
.detail-label{{font-size:0.85rem;color:var(--muted)}}
.detail-value{{font-family:var(--mono);font-size:0.9rem;font-weight:500;color:var(--ink)}}
.detail-value.warn{{color:var(--red);font-weight:600}}
.detail-section{{font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:var(--accent);padding:10px 0 4px;grid-column:span 2;border-bottom:2px solid var(--accent-light)}}

@media print {{
  .topbar,.bulk-bar,.filter-bar,.c-edit,.inc-input,.modal-overlay {{display:none!important}}
  .view{{display:flex!important;overflow:visible!important;page-break-after:always}}
  table{{font-size:11px}}
}}
</style>
</head>
<body>
<header class="topbar">
  <div class="brand">
    <svg viewBox="0 0 32 32"><path d="M4 28 L4 14 L16 5 L28 14 L28 28 L20 28 L20 19 L12 19 L12 28 Z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>
    Portfolio Manager
  </div>
  <nav class="tabs">
    <button class="tab is-active" data-tab="planner">Rent Planner</button>
    <button class="tab" data-tab="properties">Properties <span class="tab-badge">{s['total_properties']}</span></button>
    <button class="tab" data-tab="portfolio">Portfolio</button>
    <button class="tab" data-tab="market">Market</button>
  </nav>
  <div class="topbar-right">
    <button class="btn" onclick="exportCSV()">Export CSV</button>
  </div>
</header>

<!-- Detail modal -->
<div class="modal-overlay" id="modal" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <div class="modal-header">
      <div><h2 id="m-name"></h2><p class="modal-sub" id="m-location"></p></div>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    <div class="modal-body">
      <div class="detail-grid">
        <div class="detail-section">Property</div>
        <div class="detail-row"><span class="detail-label">Type</span><span class="detail-value" id="m-type"></span></div>
        <div class="detail-row"><span class="detail-label">Units</span><span class="detail-value" id="m-units"></span></div>
        <div class="detail-row"><span class="detail-label">Occupancy</span><span class="detail-value" id="m-occ"></span></div>
        <div class="detail-row"><span class="detail-label">Year acquired</span><span class="detail-value" id="m-year"></span></div>

        <div class="detail-section">Rent</div>
        <div class="detail-row"><span class="detail-label">Current rent</span><span class="detail-value" id="m-rent"></span></div>
        <div class="detail-row"><span class="detail-label">FMR 2BR (market comp)</span><span class="detail-value" id="m-fmr"></span></div>
        <div class="detail-row"><span class="detail-label">AMI ceiling</span><span class="detail-value" id="m-ceil"></span></div>
        <div class="detail-row"><span class="detail-label">Headroom to ceiling</span><span class="detail-value" id="m-headroom"></span></div>

        <div class="detail-section">Expenses (per unit/mo)</div>
        <div class="detail-row"><span class="detail-label">Insurance</span><span class="detail-value" id="m-ins"></span></div>
        <div class="detail-row"><span class="detail-label">Taxes</span><span class="detail-value" id="m-tax"></span></div>
        <div class="detail-row"><span class="detail-label">Maintenance</span><span class="detail-value" id="m-maint"></span></div>
        <div class="detail-row"><span class="detail-label">Management</span><span class="detail-value" id="m-mgmt"></span></div>
        <div class="detail-row"><span class="detail-label"><b>Total OpEx</b></span><span class="detail-value" id="m-opex"></span></div>

        <div class="detail-section">Financials (annual)</div>
        <div class="detail-row"><span class="detail-label">Revenue</span><span class="detail-value" id="m-rev"></span></div>
        <div class="detail-row"><span class="detail-label">NOI</span><span class="detail-value" id="m-noi"></span></div>
        <div class="detail-row"><span class="detail-label">Debt service</span><span class="detail-value" id="m-ds"></span></div>
        <div class="detail-row"><span class="detail-label">Cash flow</span><span class="detail-value" id="m-cf"></span></div>
        <div class="detail-row"><span class="detail-label">DSCR</span><span class="detail-value" id="m-dscr"></span></div>
        <div class="detail-row"><span class="detail-label">Cash-on-cash</span><span class="detail-value" id="m-coc"></span></div>
        <div class="detail-row"><span class="detail-label">Acquisition price</span><span class="detail-value" id="m-acq"></span></div>
      </div>
    </div>
  </div>
</div>

<main class="page">

<!-- ==================== RENT PLANNER ==================== -->
<section class="view is-active" data-view="planner">
  <header class="page-head">
    <div>
      <h1>Annual Rent Planner</h1>
      <p class="sub">{today.year + 1} increases · {s['total_properties']} properties · click any row for details</p>
    </div>
  </header>
  <div class="kpi-strip">
    <div class="kpi"><p class="kpi-label">Revenue impact</p><p class="kpi-val" id="kpi-rev-delta">—</p><p class="kpi-note" id="kpi-rev-note"></p></div>
    <div class="kpi"><p class="kpi-label">NOI impact</p><p class="kpi-val" id="kpi-noi-delta">—</p><p class="kpi-note" id="kpi-noi-note"></p></div>
    <div class="kpi"><p class="kpi-label">At AMI ceiling</p><p class="kpi-val" id="kpi-ceiling">—</p><p class="kpi-note" id="kpi-ceil-note"></p></div>
    <div class="kpi"><p class="kpi-label">Avg new rent</p><p class="kpi-val" id="kpi-new-rent">—</p><p class="kpi-note" id="kpi-rent-note"></p></div>
  </div>
  <div class="bulk-bar">
    <label>Bulk set:</label>
    <select id="bulk-scope"><option value="all">All</option><option value="mhp_lot">MHP</option><option value="lihtc_apartment">LIHTC</option><option value="market_apartment">Market</option></select>
    <input type="number" id="bulk-pct" value="3" min="-10" max="30" step="0.5"/><label>%</label>
    <button class="btn btn-primary" onclick="bulkApply()">Apply</button>
    <span style="flex:1"></span>
    <select id="filter-state" onchange="filterPlanner()"><option value="">All states</option></select>
    <select id="filter-type" onchange="filterPlanner()"><option value="">All types</option></select>
  </div>
  <div class="table-wrap">
    <table id="planner-table">
      <thead><tr><th style="min-width:180px">Property</th><th>Type</th><th>Units</th><th>Current rent</th><th style="min-width:80px">Increase %</th><th>Proposed</th></tr></thead>
      <tbody>{planner_rows}</tbody>
    </table>
  </div>
</section>

<!-- ==================== PROPERTIES ==================== -->
<section class="view" data-view="properties">
  <header class="page-head">
    <div>
      <h1>Properties</h1>
      <p class="sub">{s['total_properties']} properties · click any row for details</p>
    </div>
    <div class="filter-bar">
      <select id="prop-filter-state" onchange="filterProps()"><option value="">All states</option></select>
      <select id="prop-filter-type" onchange="filterProps()"><option value="">All types</option></select>
    </div>
  </header>
  <div class="table-wrap">
    <table id="props-table">
      <thead><tr><th style="min-width:180px">Property</th><th>Type</th><th>Units</th><th>Rent</th><th>NOI</th></tr></thead>
      <tbody>{prop_rows}</tbody>
    </table>
  </div>
</section>

<!-- ==================== PORTFOLIO ==================== -->
<section class="view" data-view="portfolio">
  <header class="page-head"><div><h1>Portfolio</h1><p class="sub">{today.strftime('%B %Y')}</p></div></header>
  <div class="kpi-strip" style="grid-template-columns:repeat(5,1fr)">
    <div class="kpi"><p class="kpi-label">Properties</p><p class="kpi-val">{s['total_properties']}</p><p class="kpi-note">{len(s['states'])} states</p></div>
    <div class="kpi"><p class="kpi-label">Units</p><p class="kpi-val">{s['total_units']:,}</p></div>
    <div class="kpi"><p class="kpi-label">Avg rent</p><p class="kpi-val">${s['avg_rent']:,.0f}</p></div>
    <div class="kpi"><p class="kpi-label">Total NOI</p><p class="kpi-val">${s['total_noi']/1e6:,.1f}M</p></div>
    <div class="kpi"><p class="kpi-label">Restricted</p><p class="kpi-val">{s['restricted_count']}</p><p class="kpi-note">{s['restricted_count']/s['total_properties']*100:.0f}% of portfolio</p></div>
  </div>
  <div class="chart-row">
    <div class="chart-panel"><h3>Units by type</h3><div id="chart-comp"></div></div>
    <div class="chart-panel"><h3>Preservation pipeline</h3><div id="chart-pres"></div></div>
  </div>
</section>

<!-- ==================== MARKET ==================== -->
<section class="view" data-view="market">
  <header class="page-head"><div><h1>Market</h1><p class="sub">HUD FY 2026 · IRS migration FY 2022–23</p></div></header>
  <div class="chart-row">
    <div class="chart-panel"><h3>FMR trajectory — top counties</h3><div id="chart-fmr"></div></div>
    <div class="chart-panel"><h3>Expiration buckets</h3><div id="chart-pres2"></div></div>
  </div>
</section>

</main>

<script>
const DATA = {json.dumps(data)};
const fmt = n => n < 0 ? '-$'+Math.abs(n).toLocaleString() : '$'+n.toLocaleString();
const fmtM = n => {{ const s = n >= 0 ? '+' : ''; return s+'$'+(n/1e6).toFixed(2)+'M'; }};

// Tabs
document.querySelectorAll('.tab').forEach(t => {{
  t.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('is-active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('is-active'));
    t.classList.add('is-active');
    document.querySelector('[data-view="'+t.dataset.tab+'"]').classList.add('is-active');
    setTimeout(() => window.dispatchEvent(new Event('resize')), 50);
  }});
}});

// Filters
const states = DATA.summary.states;
['filter-state','prop-filter-state'].forEach(id => {{
  const sel = document.getElementById(id);
  states.forEach(s => {{ const o = document.createElement('option'); o.value=s; o.textContent=s; sel.appendChild(o); }});
}});
['filter-type','prop-filter-type'].forEach(id => {{
  const sel = document.getElementById(id);
  [['mhp_lot','MHP'],['lihtc_apartment','LIHTC'],['market_apartment','Market']].forEach(([v,l]) => {{
    const o = document.createElement('option'); o.value=v; o.textContent=l; sel.appendChild(o);
  }});
}});

// Modal
function openModal(row) {{
  const d = row.dataset;
  const typeLabels = {{mhp_lot:'MHP Lot Rent',lihtc_apartment:'LIHTC Apartment',market_apartment:'Market Rate'}};
  document.getElementById('m-name').textContent = row.querySelector('.c-name b').textContent;
  document.getElementById('m-location').textContent = (d.county||'') + ', ' + d.state;
  document.getElementById('m-type').textContent = typeLabels[d.type] || d.type;
  document.getElementById('m-units').textContent = d.units;
  document.getElementById('m-occ').textContent = d.occ + '%';
  document.getElementById('m-year').textContent = d.yearacq;
  document.getElementById('m-rent').textContent = '$'+Number(d.rent).toLocaleString();
  document.getElementById('m-fmr').textContent = '$'+Number(d.fmr).toLocaleString();
  const ceilEl = document.getElementById('m-ceil');
  if (d.amiRent && d.amiRent !== '') {{
    ceilEl.textContent = '$'+Number(d.amiRent).toLocaleString(undefined,{{maximumFractionDigits:0}}) + ' ('+d.amiPct+'% AMI)';
    const headroom = parseFloat(d.headroom);
    if (!isNaN(headroom) && headroom < 5) ceilEl.classList.add('warn'); else ceilEl.classList.remove('warn');
  }} else {{ ceilEl.textContent = 'None (market rate)'; ceilEl.classList.remove('warn'); }}
  document.getElementById('m-headroom').textContent = d.headroom ? d.headroom+'%' : '—';
  document.getElementById('m-ins').textContent = '$'+Number(d.ins).toFixed(0);
  document.getElementById('m-tax').textContent = '$'+Number(d.tax).toFixed(0);
  document.getElementById('m-maint').textContent = '$'+Number(d.maint).toFixed(0);
  document.getElementById('m-mgmt').textContent = '$'+Number(d.mgmt).toFixed(0);
  document.getElementById('m-opex').textContent = '$'+Number(d.opex).toFixed(0);
  document.getElementById('m-rev').textContent = fmt(Math.round(+d.rent * +d.occupied * 12));
  document.getElementById('m-noi').textContent = fmt(Math.round(+d.noi));
  document.getElementById('m-ds').textContent = fmt(Math.round(+d.ds));
  document.getElementById('m-cf').textContent = fmt(Math.round(+d.cashflow));
  document.getElementById('m-dscr').textContent = d.dscr ? (+d.dscr).toFixed(2)+'x' : '—';
  document.getElementById('m-coc').textContent = d.coc ? (+d.coc).toFixed(1)+'%' : '—';
  document.getElementById('m-acq').textContent = '$'+(+d.acq/1e6).toFixed(2)+'M';
  document.getElementById('modal').classList.add('open');
}}
function closeModal() {{ document.getElementById('modal').classList.remove('open'); }}
document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeModal(); }});

// Planner calc
function recalcPlanner() {{
  let totalRevD=0, totalNOID=0, ceilCt=0, newRentSum=0, oldRentSum=0, n=0;
  document.querySelectorAll('#planner-table tbody tr').forEach(row => {{
    if (row.style.display==='none') return;
    const rent=+row.dataset.rent, occ=+row.dataset.occupied, noi=+row.dataset.noi;
    const ceiling=+row.dataset.ceiling, restricted=+row.dataset.restricted;
    const inc = parseFloat(row.querySelector('.inc-input').value)||0;
    let proposed = rent*(1+inc/100);
    let atCeil = false;
    if (restricted && proposed > ceiling && ceiling < 99999) {{ proposed=ceiling; atCeil=true; }}
    const revD = (proposed-rent)*occ*12;
    row.querySelector('.c-proposed').textContent = '$'+Math.round(proposed).toLocaleString();
    row.classList.toggle('at-ceiling', atCeil);
    totalRevD+=revD; totalNOID+=revD; if(atCeil)ceilCt++; newRentSum+=proposed; oldRentSum+=rent; n++;
  }});
  document.getElementById('kpi-rev-delta').textContent = fmtM(totalRevD);
  document.getElementById('kpi-rev-note').textContent = 'annual revenue'; document.getElementById('kpi-rev-note').className='kpi-note '+(totalRevD>=0?'up':'down');
  document.getElementById('kpi-noi-delta').textContent = fmtM(totalNOID);
  document.getElementById('kpi-noi-note').textContent = 'projected change'; document.getElementById('kpi-noi-note').className='kpi-note '+(totalNOID>=0?'up':'down');
  document.getElementById('kpi-ceiling').textContent = ceilCt;
  document.getElementById('kpi-ceil-note').textContent = ceilCt>0?'capped at AMI limit':'none at ceiling';
  document.getElementById('kpi-ceil-note').className='kpi-note '+(ceilCt>0?'down':'up');
  document.getElementById('kpi-new-rent').textContent = n>0?'$'+Math.round(newRentSum/n).toLocaleString():'—';
  document.getElementById('kpi-rent-note').textContent = n>0?'from $'+Math.round(oldRentSum/n).toLocaleString():'';
}}

function bulkApply() {{
  const scope=document.getElementById('bulk-scope').value, pct=document.getElementById('bulk-pct').value;
  document.querySelectorAll('#planner-table tbody tr').forEach(row => {{
    if(scope==='all'||row.dataset.type===scope) row.querySelector('.inc-input').value=pct;
  }});
  recalcPlanner();
}}

function filterPlanner() {{
  const state=document.getElementById('filter-state').value, type=document.getElementById('filter-type').value;
  document.querySelectorAll('#planner-table tbody tr').forEach(row => {{
    row.style.display=(!state||row.dataset.state===state)&&(!type||row.dataset.type===type)?'':'none';
  }});
  recalcPlanner();
}}
function filterProps() {{
  const state=document.getElementById('prop-filter-state').value, type=document.getElementById('prop-filter-type').value;
  document.querySelectorAll('#props-table tbody tr').forEach(row => {{
    row.style.display=(!state||row.dataset.state===state)&&(!type||row.dataset.type===type)?'':'none';
  }});
}}

document.querySelectorAll('.inc-input').forEach(inp => inp.addEventListener('input', recalcPlanner));

function exportCSV() {{
  const rows=[['Property','State','Type','Units','Current Rent','Increase %','Proposed Rent','FMR','AMI Ceiling','NOI','Debt Service','DSCR']];
  document.querySelectorAll('#planner-table tbody tr').forEach(row => {{
    if(row.style.display==='none')return;
    const d=row.dataset, inc=row.querySelector('.inc-input').value;
    let proposed=+d.rent*(1+(+inc)/100);
    if(+d.restricted&&proposed>+d.ceiling&&+d.ceiling<99999) proposed=+d.ceiling;
    rows.push([row.querySelector('.c-name b').textContent,d.state,d.type,d.units,d.rent,inc,proposed.toFixed(0),d.fmr,d.ceiling==='99999'?'':d.ceiling,d.noi,d.ds,d.dscr]);
  }});
  const blob=new Blob([rows.map(r=>r.join(',')).join('\\n')],{{type:'text/csv'}});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob);
  a.download='rent-plan-'+new Date().toISOString().slice(0,10)+'.csv'; a.click();
}}

// Charts
const cfg={{responsive:true,displayModeBar:false}};
const lB={{font:{{family:'IBM Plex Sans',size:13,color:'#2D3748'}},paper_bgcolor:'#fff',plot_bgcolor:'#fff',margin:{{l:40,r:10,t:10,b:40}}}};

const comp=DATA.summary.by_type;
Plotly.newPlot('chart-comp',[{{x:['MHP','LIHTC','Market'],y:[comp.mhp_lot.units,comp.lihtc_apartment.units,comp.market_apartment.units],type:'bar',marker:{{color:['#1F4A3D','#B07A2A','#3F4F75']}}}}],{{...lB,height:260}},cfg);

const pres=DATA.preservation;
Plotly.newPlot('chart-pres',[{{x:Object.keys(pres),y:Object.values(pres),type:'bar',marker:{{color:['#718096','#C53030','#7A4A4A','#B07A2A','#1F4A3D']}}}}],{{...lB,height:260,xaxis:{{tickangle:-25}}}},cfg);
Plotly.newPlot('chart-pres2',[{{x:Object.keys(pres),y:Object.values(pres),type:'bar',marker:{{color:['#718096','#C53030','#7A4A4A','#B07A2A','#1F4A3D']}}}}],{{...lB,height:300,xaxis:{{tickangle:-25}}}},cfg);

const traj=DATA.fmr_trajectory.filter(r=>!r.projected);
const counties=[...new Set(traj.map(r=>r.label))];
Plotly.newPlot('chart-fmr',counties.map(c=>{{const pts=traj.filter(r=>r.label===c).sort((a,b)=>a.year-b.year);return{{x:pts.map(r=>r.year),y:pts.map(r=>r.fmr_2br),mode:'lines+markers',name:c,marker:{{size:3}}}};}}),{{...lB,height:300,legend:{{font:{{size:9}},orientation:'h',y:-0.15}}}},cfg);

recalcPlanner();
</script>
</body>
</html>"""

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html)
    print(f"v3 dashboard: {OUT_PATH} ({OUT_PATH.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
