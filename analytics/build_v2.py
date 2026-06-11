"""Build the v2 dashboard: rent-planner-first, data-dense, work-tool aesthetic."""

import json
from pathlib import Path
from datetime import date

DATA_PATH = Path(__file__).resolve().parent / "output" / "v2_data.json"
OUT_PATH = Path(__file__).resolve().parent.parent / "for-frank-and-brittney" / "demo" / "v2" / "index.html"


def main():
    data = json.loads(DATA_PATH.read_text())
    s = data["summary"]
    today = date.today()

    prop_rows = ""
    for p in data["properties"]:
        ceil_display = f"${p['ami_ceiling_rent']:,.0f}" if p['ami_ceiling_rent'] else "—"
        headroom = f"{p['headroom_pct']:+.1f}%" if p['headroom_pct'] is not None else "—"
        dscr = f"{p['dscr']:.2f}" if p['dscr'] else "—"
        prop_rows += f"""<tr data-type="{p['type']}" data-state="{p['state']}" data-id="{p['id']}"
          data-rent="{p['current_rent']}" data-units="{p['units']}" data-occupied="{p['occupied']}"
          data-noi="{p['noi']}" data-opex="{p['expenses']['total']}" data-ds="{p['debt_service']}"
          data-ceiling="{p['ami_ceiling_rent'] or 99999}" data-restricted="{1 if p['rent_restricted'] else 0}"
          data-acq="{p['acquisition_price']}">
          <td class="c-name"><b>{p['name']}</b><span>{p['county']}, {p['state']}</span></td>
          <td class="c-type"><span class="pill pill-{p['type']}">{p['type_label']}</span></td>
          <td class="c-num">{p['units']}</td>
          <td class="c-num">{p['occupancy_pct']:.0f}%</td>
          <td class="c-money">${p['current_rent']:,.0f}</td>
          <td class="c-money c-fmr">${p['fmr_2br']:,.0f}</td>
          <td class="c-money c-ceil">{ceil_display}</td>
          <td class="c-num c-headroom">{headroom}</td>
          <td class="c-edit"><input type="number" class="inc-input" value="3" min="-10" max="30" step="0.5" /></td>
          <td class="c-money c-proposed">—</td>
          <td class="c-money c-proj-noi">—</td>
          <td class="c-num c-proj-dscr">—</td>
        </tr>"""

    # Properties table (simpler)
    properties_rows = ""
    for p in data["properties"]:
        ceil_display = f"${p['ami_ceiling_rent']:,.0f}" if p['ami_ceiling_rent'] else "—"
        dscr = f"{p['dscr']:.2f}" if p['dscr'] else "—"
        properties_rows += f"""<tr data-type="{p['type']}" data-state="{p['state']}">
          <td class="c-name"><b>{p['name']}</b><span>{p['county']}, {p['state']}</span></td>
          <td><span class="pill pill-{p['type']}">{p['type_label']}</span></td>
          <td class="c-num">{p['units']}</td>
          <td class="c-num">{p['occupancy_pct']:.0f}%</td>
          <td class="c-money">${p['current_rent']:,.0f}</td>
          <td class="c-money">{ceil_display}</td>
          <td class="c-money">${p['noi']:,.0f}</td>
          <td class="c-num">{dscr}</td>
          <td class="c-money">${p['cash_flow']:,.0f}</td>
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
  --accent: #1F4A3D;
  --accent-light: #E6EDE9;
  --brass: #B07A2A;
  --brass-light: #F1E6D0;
  --slate: #3F4F75;
  --red: #C53030;
  --red-light: #FED7D7;
  --green: #276749;
  --green-light: #C6F6D5;
  --ink: #1A202C;
  --text: #2D3748;
  --muted: #718096;
  --border: #E2E8F0;
  --border-light: #EDF2F7;
  --bg: #F7FAFC;
  --card: #FFFFFF;
  --sans: "IBM Plex Sans","Helvetica Neue",Arial,sans-serif;
  --mono: "IBM Plex Mono","SF Mono",Menlo,monospace;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{height:100vh;overflow:hidden;background:var(--bg);color:var(--text);font-family:var(--sans);font-size:13.5px;line-height:1.45}}
body{{display:flex;flex-direction:column}}
.topbar{{flex:0 0 auto;display:flex;align-items:center;justify-content:space-between;padding:10px 20px;background:var(--card);border-bottom:1px solid var(--border);gap:16px}}
.brand{{font-weight:600;font-size:1rem;color:var(--accent);display:flex;align-items:center;gap:8px}}
.brand svg{{width:24px;height:24px}}
.tabs{{display:flex;gap:2px}}
.tab{{appearance:none;border:0;background:transparent;font-family:var(--sans);font-size:0.85rem;font-weight:500;color:var(--muted);padding:8px 14px;border-radius:6px;cursor:pointer}}
.tab:hover{{background:var(--bg);color:var(--text)}}
.tab.is-active{{background:var(--accent);color:#fff}}
.tab-badge{{font-family:var(--mono);font-size:0.7rem;background:rgba(255,255,255,.2);padding:1px 5px;border-radius:8px;margin-left:4px}}
.topbar-right{{display:flex;gap:8px;align-items:center}}
.btn{{appearance:none;border:1px solid var(--border);background:var(--card);font-family:var(--sans);font-size:0.82rem;font-weight:500;padding:6px 12px;border-radius:5px;cursor:pointer;color:var(--text)}}
.btn:hover{{border-color:var(--accent);color:var(--accent)}}
.btn-primary{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.btn-primary:hover{{background:#143A2E}}

.page{{flex:1;min-height:0;position:relative}}
.view{{display:none;height:100%;flex-direction:column;padding:14px 20px;gap:12px;overflow-y:auto}}
.view.is-active{{display:flex}}

.page-head{{flex:0 0 auto;display:flex;justify-content:space-between;align-items:flex-end;gap:16px}}
.page-head h1{{font-size:1.35rem;font-weight:600;color:var(--ink)}}
.page-head .sub{{font-size:0.85rem;color:var(--muted);margin-top:2px}}

/* KPIs */
.kpi-strip{{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;flex:0 0 auto}}
.kpi{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px 14px}}
.kpi-label{{font-size:0.72rem;font-weight:500;color:var(--muted);text-transform:uppercase;letter-spacing:0.06em}}
.kpi-val{{font-family:var(--mono);font-size:1.4rem;font-weight:600;color:var(--ink);margin:4px 0 2px}}
.kpi-note{{font-size:0.75rem;color:var(--muted)}}
.kpi-note.up{{color:var(--green)}}
.kpi-note.down{{color:var(--red)}}

/* Bulk controls */
.bulk-bar{{display:flex;gap:10px;align-items:center;flex:0 0 auto;padding:8px 12px;background:var(--card);border:1px solid var(--border);border-radius:8px;flex-wrap:wrap}}
.bulk-bar label{{font-size:0.8rem;font-weight:500;color:var(--text)}}
.bulk-bar select,.bulk-bar input[type="number"]{{font-family:var(--mono);font-size:0.85rem;padding:4px 8px;border:1px solid var(--border);border-radius:4px;background:var(--card)}}
.bulk-bar input[type="number"]{{width:70px}}

/* Data table */
.table-wrap{{flex:1;min-height:0;overflow:auto;background:var(--card);border:1px solid var(--border);border-radius:8px}}
table{{width:100%;border-collapse:collapse;font-size:0.82rem}}
thead th{{position:sticky;top:0;background:var(--bg);border-bottom:2px solid var(--border);padding:8px 10px;text-align:left;font-weight:600;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--muted);white-space:nowrap;z-index:2}}
tbody td{{padding:7px 10px;border-bottom:1px solid var(--border-light);vertical-align:middle}}
tbody tr:hover{{background:#F0FFF4}}
.c-name b{{display:block;font-weight:500;color:var(--ink)}}
.c-name span{{display:block;font-size:0.75rem;color:var(--muted)}}
.c-num{{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums}}
.c-money{{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums}}
.c-edit{{text-align:center}}
.inc-input{{width:58px;font-family:var(--mono);font-size:0.85rem;padding:3px 6px;border:1px solid var(--border);border-radius:4px;text-align:right;background:var(--card)}}
.inc-input:focus{{outline:2px solid var(--accent);border-color:var(--accent)}}
.pill{{display:inline-block;font-size:0.7rem;font-weight:500;padding:2px 8px;border-radius:10px}}
.pill-mhp_lot{{background:var(--accent-light);color:var(--accent)}}
.pill-lihtc_apartment{{background:var(--brass-light);color:var(--brass)}}
.pill-market_apartment{{background:#E2E8F0;color:var(--slate)}}
tr.at-ceiling td{{background:var(--red-light)}}
tr.at-ceiling .c-proposed{{color:var(--red);font-weight:600}}

/* Filters */
.filter-bar{{display:flex;gap:8px;align-items:center;flex:0 0 auto}}
.filter-bar select{{font-size:0.82rem;padding:5px 8px;border:1px solid var(--border);border-radius:5px}}

/* Charts */
.chart-row{{display:grid;grid-template-columns:1fr 1fr;gap:12px;flex:0 0 auto}}
.chart-panel{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:14px}}
.chart-panel h3{{font-size:0.85rem;font-weight:600;margin-bottom:8px}}

@media print {{
  .topbar,.bulk-bar,.filter-bar,.c-edit,.inc-input {{display:none!important}}
  .view{{display:flex!important;overflow:visible!important;page-break-after:always}}
  table{{font-size:10px}}
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

<main class="page">
<!-- ==================== RENT PLANNER ==================== -->
<section class="view is-active" data-view="planner">
  <header class="page-head">
    <div>
      <h1>Annual Rent Planner</h1>
      <p class="sub">{today.year + 1} rent increases · {s['total_properties']} properties · {s['total_units']:,} units</p>
    </div>
  </header>

  <div class="kpi-strip" id="planner-kpis">
    <div class="kpi"><p class="kpi-label">Revenue impact</p><p class="kpi-val" id="kpi-rev-delta">—</p><p class="kpi-note" id="kpi-rev-note"></p></div>
    <div class="kpi"><p class="kpi-label">NOI impact</p><p class="kpi-val" id="kpi-noi-delta">—</p><p class="kpi-note" id="kpi-noi-note"></p></div>
    <div class="kpi"><p class="kpi-label">Avg increase</p><p class="kpi-val" id="kpi-avg-inc">—</p><p class="kpi-note" id="kpi-avg-note"></p></div>
    <div class="kpi"><p class="kpi-label">At AMI ceiling</p><p class="kpi-val" id="kpi-ceiling">—</p><p class="kpi-note" id="kpi-ceil-note"></p></div>
    <div class="kpi"><p class="kpi-label">Avg DSCR</p><p class="kpi-val" id="kpi-dscr">—</p><p class="kpi-note" id="kpi-dscr-note"></p></div>
    <div class="kpi"><p class="kpi-label">Avg rent (new)</p><p class="kpi-val" id="kpi-new-rent">—</p><p class="kpi-note" id="kpi-rent-note"></p></div>
  </div>

  <div class="bulk-bar">
    <label>Bulk set:</label>
    <select id="bulk-scope">
      <option value="all">All properties</option>
      <option value="mhp_lot">MHP only</option>
      <option value="lihtc_apartment">LIHTC only</option>
      <option value="market_apartment">Market only</option>
    </select>
    <input type="number" id="bulk-pct" value="3" min="-10" max="30" step="0.5"/>
    <label>%</label>
    <button class="btn btn-primary" onclick="bulkApply()">Apply</button>
    <span style="flex:1"></span>
    <label style="color:var(--muted)">Filter:</label>
    <select id="filter-state" onchange="filterPlanner()"><option value="">All states</option></select>
    <select id="filter-type" onchange="filterPlanner()"><option value="">All types</option></select>
  </div>

  <div class="table-wrap">
    <table id="planner-table">
      <thead>
        <tr>
          <th style="min-width:180px">Property</th>
          <th>Type</th>
          <th>Units</th>
          <th>Occ</th>
          <th>Current rent</th>
          <th>FMR comp</th>
          <th>AMI ceiling</th>
          <th>Headroom</th>
          <th style="min-width:80px">Increase %</th>
          <th>Proposed rent</th>
          <th>Proj. NOI</th>
          <th>DSCR</th>
        </tr>
      </thead>
      <tbody>{prop_rows}</tbody>
    </table>
  </div>
</section>

<!-- ==================== PROPERTIES ==================== -->
<section class="view" data-view="properties">
  <header class="page-head">
    <div>
      <h1>Properties</h1>
      <p class="sub">{s['total_properties']} properties · ${s['total_value']:.0f}M portfolio</p>
    </div>
    <div class="filter-bar">
      <select id="prop-filter-state" onchange="filterProps()"><option value="">All states</option></select>
      <select id="prop-filter-type" onchange="filterProps()"><option value="">All types</option></select>
    </div>
  </header>
  <div class="table-wrap">
    <table id="props-table">
      <thead><tr>
        <th style="min-width:180px">Property</th><th>Type</th><th>Units</th><th>Occ</th>
        <th>Rent</th><th>AMI ceiling</th><th>NOI</th><th>DSCR</th><th>Cash flow</th>
      </tr></thead>
      <tbody>{properties_rows}</tbody>
    </table>
  </div>
</section>

<!-- ==================== PORTFOLIO ==================== -->
<section class="view" data-view="portfolio">
  <header class="page-head"><div><h1>Portfolio summary</h1><p class="sub">{today.strftime('%B %Y')}</p></div></header>
  <div class="kpi-strip" style="grid-template-columns:repeat(5,1fr)">
    <div class="kpi"><p class="kpi-label">Properties</p><p class="kpi-val">{s['total_properties']}</p><p class="kpi-note">{len(s['states'])} states</p></div>
    <div class="kpi"><p class="kpi-label">Units</p><p class="kpi-val">{s['total_units']:,}</p><p class="kpi-note">{s['by_type']['mhp_lot']['units']:,} MHP · {s['by_type']['lihtc_apartment']['units']:,} LIHTC</p></div>
    <div class="kpi"><p class="kpi-label">Avg rent</p><p class="kpi-val">${s['avg_rent']:,.0f}</p><p class="kpi-note">MHP ${s['by_type']['mhp_lot']['avg_rent']:,} · LIHTC ${s['by_type']['lihtc_apartment']['avg_rent']:,}</p></div>
    <div class="kpi"><p class="kpi-label">Total NOI</p><p class="kpi-val">${s['total_noi']/1e6:,.1f}M</p><p class="kpi-note">Annual</p></div>
    <div class="kpi"><p class="kpi-label">Restricted</p><p class="kpi-val">{s['restricted_count']}</p><p class="kpi-note">{s['restricted_count']/s['total_properties']*100:.0f}% of portfolio</p></div>
  </div>
  <div class="chart-row">
    <div class="chart-panel"><h3>Units by state &amp; type</h3><div id="chart-composition"></div></div>
    <div class="chart-panel"><h3>Preservation pipeline</h3><div id="chart-pres"></div></div>
  </div>
</section>

<!-- ==================== MARKET ==================== -->
<section class="view" data-view="market">
  <header class="page-head"><div><h1>Market reference</h1><p class="sub">HUD FY 2026 data · IRS migration FY 2022–23</p></div></header>
  <div class="chart-row">
    <div class="chart-panel"><h3>FMR trajectory — top migration counties</h3><div id="chart-fmr"></div></div>
    <div class="chart-panel"><h3>Preservation expiration buckets</h3><div id="chart-pres2"></div></div>
  </div>
</section>
</main>

<script>
const DATA = {json.dumps(data)};

// Tab switching
document.querySelectorAll('.tab').forEach(t => {{
  t.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('is-active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('is-active'));
    t.classList.add('is-active');
    document.querySelector('[data-view="'+t.dataset.tab+'"]').classList.add('is-active');
    setTimeout(() => window.dispatchEvent(new Event('resize')), 50);
  }});
}});

// Populate filter dropdowns
const states = DATA.summary.states;
const types = [{{"mhp_lot":"MHP"}},{{"lihtc_apartment":"LIHTC"}},{{"market_apartment":"Market"}}];
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

// Planner calculation
function recalcPlanner() {{
  let totalRevDelta=0, totalNOIDelta=0, totalNewRent=0, totalOldRent=0, ceilCount=0, dscrSum=0, dscrN=0, incSum=0, incN=0;
  document.querySelectorAll('#planner-table tbody tr').forEach(row => {{
    if (row.style.display === 'none') return;
    const rent = +row.dataset.rent;
    const units = +row.dataset.units;
    const occ = +row.dataset.occupied;
    const noi = +row.dataset.noi;
    const opex = +row.dataset.opex;
    const ds = +row.dataset.ds;
    const ceiling = +row.dataset.ceiling;
    const restricted = +row.dataset.restricted;
    const inc = parseFloat(row.querySelector('.inc-input').value) || 0;

    let proposed = rent * (1 + inc/100);
    let atCeiling = false;
    if (restricted && proposed > ceiling && ceiling < 99999) {{
      proposed = ceiling;
      atCeiling = true;
    }}

    const revDelta = (proposed - rent) * occ * 12;
    const projNOI = noi + revDelta;
    const dscr = ds > 0 ? projNOI / ds : null;

    row.querySelector('.c-proposed').textContent = '$' + Math.round(proposed).toLocaleString();
    row.querySelector('.c-proj-noi').textContent = '$' + Math.round(projNOI).toLocaleString();
    row.querySelector('.c-proj-dscr').textContent = dscr ? dscr.toFixed(2) : '—';
    row.classList.toggle('at-ceiling', atCeiling);

    totalRevDelta += revDelta;
    totalNOIDelta += projNOI - noi;
    totalNewRent += proposed;
    totalOldRent += rent;
    if (atCeiling) ceilCount++;
    if (dscr) {{ dscrSum += dscr; dscrN++; }}
    incSum += inc; incN++;
  }});

  const sign = totalRevDelta >= 0 ? '+' : '';
  document.getElementById('kpi-rev-delta').textContent = sign + '$' + (totalRevDelta/1e6).toFixed(2) + 'M';
  document.getElementById('kpi-rev-note').textContent = 'annual revenue ' + (totalRevDelta >= 0 ? 'increase' : 'decrease');
  document.getElementById('kpi-rev-note').className = 'kpi-note ' + (totalRevDelta >= 0 ? 'up' : 'down');

  document.getElementById('kpi-noi-delta').textContent = sign + '$' + (totalNOIDelta/1e6).toFixed(2) + 'M';
  document.getElementById('kpi-noi-note').textContent = 'projected NOI change';
  document.getElementById('kpi-noi-note').className = 'kpi-note ' + (totalNOIDelta >= 0 ? 'up' : 'down');

  document.getElementById('kpi-avg-inc').textContent = incN > 0 ? (incSum/incN).toFixed(1) + '%' : '—';
  document.getElementById('kpi-avg-note').textContent = 'across ' + incN + ' properties';

  document.getElementById('kpi-ceiling').textContent = ceilCount;
  document.getElementById('kpi-ceil-note').textContent = ceilCount > 0 ? 'rent capped at AMI limit' : 'none at ceiling';
  document.getElementById('kpi-ceil-note').className = 'kpi-note ' + (ceilCount > 0 ? 'down' : 'up');

  document.getElementById('kpi-dscr').textContent = dscrN > 0 ? (dscrSum/dscrN).toFixed(2) + 'x' : '—';
  const avgDscr = dscrN > 0 ? dscrSum/dscrN : 0;
  document.getElementById('kpi-dscr-note').textContent = avgDscr < 1.2 ? 'below 1.2x target' : 'healthy';
  document.getElementById('kpi-dscr-note').className = 'kpi-note ' + (avgDscr >= 1.2 ? 'up' : 'down');

  document.getElementById('kpi-new-rent').textContent = incN > 0 ? '$' + Math.round(totalNewRent/incN).toLocaleString() : '—';
  document.getElementById('kpi-rent-note').textContent = 'from $' + Math.round(totalOldRent/incN).toLocaleString() + ' current';
}}

// Bulk apply
function bulkApply() {{
  const scope = document.getElementById('bulk-scope').value;
  const pct = document.getElementById('bulk-pct').value;
  document.querySelectorAll('#planner-table tbody tr').forEach(row => {{
    if (scope === 'all' || row.dataset.type === scope) {{
      row.querySelector('.inc-input').value = pct;
    }}
  }});
  recalcPlanner();
}}

// Filter planner
function filterPlanner() {{
  const state = document.getElementById('filter-state').value;
  const type = document.getElementById('filter-type').value;
  document.querySelectorAll('#planner-table tbody tr').forEach(row => {{
    const show = (!state || row.dataset.state === state) && (!type || row.dataset.type === type);
    row.style.display = show ? '' : 'none';
  }});
  recalcPlanner();
}}

// Filter properties
function filterProps() {{
  const state = document.getElementById('prop-filter-state').value;
  const type = document.getElementById('prop-filter-type').value;
  document.querySelectorAll('#props-table tbody tr').forEach(row => {{
    const show = (!state || row.dataset.state === state) && (!type || row.dataset.type === type);
    row.style.display = show ? '' : 'none';
  }});
}}

// Listen to inline edits
document.querySelectorAll('.inc-input').forEach(inp => {{
  inp.addEventListener('input', recalcPlanner);
}});

// CSV export
function exportCSV() {{
  const rows = [['Property','State','Type','Units','Current Rent','FMR','AMI Ceiling','Increase %','Proposed Rent','Projected NOI','DSCR']];
  document.querySelectorAll('#planner-table tbody tr').forEach(row => {{
    if (row.style.display === 'none') return;
    const cells = row.querySelectorAll('td');
    rows.push([
      cells[0].querySelector('b').textContent,
      row.dataset.state,
      cells[1].textContent.trim(),
      row.dataset.units,
      row.dataset.rent,
      cells[5].textContent.replace('$','').replace(',',''),
      cells[6].textContent.replace('$','').replace(',',''),
      row.querySelector('.inc-input').value,
      cells[9].textContent.replace('$','').replace(',',''),
      cells[10].textContent.replace('$','').replace(',',''),
      cells[11].textContent,
    ]);
  }});
  const csv = rows.map(r => r.join(',')).join('\\n');
  const blob = new Blob([csv], {{type:'text/csv'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'rent-plan-' + new Date().toISOString().slice(0,10) + '.csv';
  a.click();
}}

// Charts
const cfg = {{responsive:true, displayModeBar:false}};
const lBase = {{font:{{family:'IBM Plex Sans',size:11,color:'#2D3748'}},paper_bgcolor:'#fff',plot_bgcolor:'#fff',margin:{{l:40,r:10,t:10,b:40}}}};

// Composition chart
const compData = DATA.summary.by_type;
Plotly.newPlot('chart-composition',[
  {{x:['MHP','LIHTC','Market'],y:[compData.mhp_lot.units,compData.lihtc_apartment.units,compData.market_apartment.units],type:'bar',marker:{{color:['#1F4A3D','#B07A2A','#3F4F75']}}}}
],{{...lBase,height:280,yaxis:{{title:'Units'}}}},cfg);

// Preservation
const pres = DATA.preservation;
Plotly.newPlot('chart-pres',[{{x:Object.keys(pres),y:Object.values(pres),type:'bar',marker:{{color:['#718096','#C53030','#7A4A4A','#B07A2A','#1F4A3D']}}}}],{{...lBase,height:280,xaxis:{{tickangle:-25}}}},cfg);
Plotly.newPlot('chart-pres2',[{{x:Object.keys(pres),y:Object.values(pres),type:'bar',marker:{{color:['#718096','#C53030','#7A4A4A','#B07A2A','#1F4A3D']}}}}],{{...lBase,height:300,xaxis:{{tickangle:-25}}}},cfg);

// FMR trajectory
const traj = DATA.fmr_trajectory.filter(r => !r.projected);
const counties = [...new Set(traj.map(r => r.label))];
const fmrTraces = counties.map(c => {{
  const pts = traj.filter(r => r.label===c).sort((a,b)=>a.year-b.year);
  return {{x:pts.map(r=>r.year),y:pts.map(r=>r.fmr_2br),mode:'lines+markers',name:c,marker:{{size:3}}}};
}});
Plotly.newPlot('chart-fmr',fmrTraces,{{...lBase,height:300,legend:{{font:{{size:9}},orientation:'h',y:-0.15}}}},cfg);

// Initial calc
recalcPlanner();
</script>
</body>
</html>"""

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html)
    print(f"v2 dashboard: {OUT_PATH}")
    print(f"Size: {OUT_PATH.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
