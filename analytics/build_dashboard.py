"""Build the unified HTML dashboard: Emma's Estates aesthetic + real analytics data.

Reads analytics/output/dashboard_data.json + the Emma's Estates CSS,
produces a single self-contained HTML file with Plotly.js charts and
interactive rent-simulation sliders.
"""

import json
from pathlib import Path
from datetime import date

DATA_PATH = Path(__file__).resolve().parent / "output" / "dashboard_data.json"
CSS_PATH = Path(__file__).resolve().parent.parent / "for-frank-and-brittney" / "demo" / "emmas-estates" / "styles.css"
OUT_PATH = Path(__file__).resolve().parent.parent / "for-frank-and-brittney" / "demo" / "dashboard" / "index.html"


def main():
    data = json.loads(DATA_PATH.read_text())
    css = CSS_PATH.read_text()
    p = data["portfolio"]

    tones = ["forest", "brass", "slate", "forest", "brass", "slate", "forest", "brass", "slate", "forest", "brass", "slate"]
    type_labels = {"mhp_lot": "MHP", "lihtc_apartment": "LIHTC", "market_apartment": "Market"}
    type_colors = {"mhp_lot": "var(--accent)", "lihtc_apartment": "var(--brass)", "market_apartment": "var(--slate)"}

    svg_houses = [
        '<path d="M20 80 L20 50 L55 28 L90 50 L90 80 Z" fill="currentColor" opacity=".55"/><path d="M90 80 L90 58 L120 42 L150 58 L150 80 Z" fill="currentColor" opacity=".78"/><rect x="46" y="58" width="10" height="22" fill="#FAF7F0"/><rect x="32" y="56" width="8" height="8" fill="#FAF7F0" opacity=".9"/><rect x="110" y="62" width="6" height="18" fill="#FAF7F0"/>',
        '<rect x="30" y="40" width="100" height="40" fill="currentColor" opacity=".72"/><path d="M30 40 L80 22 L130 40 Z" fill="currentColor" opacity=".55"/><rect x="44" y="52" width="10" height="14" fill="#FAF7F0"/><rect x="64" y="52" width="10" height="14" fill="#FAF7F0"/><rect x="84" y="52" width="10" height="14" fill="#FAF7F0"/><rect x="74" y="66" width="12" height="14" fill="#FAF7F0" opacity=".75"/>',
        '<path d="M14 80 L14 46 L34 46 L34 30 L100 30 L100 46 L146 46 L146 80 Z" fill="currentColor" opacity=".68"/><rect x="44" y="42" width="14" height="14" fill="#FAF7F0"/><rect x="64" y="42" width="14" height="14" fill="#FAF7F0"/><rect x="84" y="42" width="14" height="14" fill="#FAF7F0"/><rect x="108" y="58" width="10" height="22" fill="#FAF7F0"/>',
        '<rect x="14" y="38" width="32" height="42" fill="currentColor" opacity=".7"/><rect x="48" y="34" width="32" height="46" fill="currentColor" opacity=".58"/><rect x="82" y="40" width="32" height="40" fill="currentColor" opacity=".75"/><rect x="116" y="36" width="32" height="44" fill="currentColor" opacity=".62"/><rect x="22" y="50" width="6" height="10" fill="#FAF7F0"/><rect x="56" y="46" width="6" height="10" fill="#FAF7F0"/><rect x="90" y="52" width="6" height="10" fill="#FAF7F0"/><rect x="124" y="48" width="6" height="10" fill="#FAF7F0"/>',
    ]

    listing_cards = ""
    for i, prop in enumerate(data["listings"]):
        tone = tones[i % len(tones)]
        svg = svg_houses[i % len(svg_houses)]
        ptype = type_labels.get(prop.get("property_type", ""), "")
        tag_class = "muted" if ptype == "Market" else ""
        listing_cards += f"""
        <article class="lcard">
          <div class="listing-img" data-tone="{tone}">
            <svg viewBox="0 0 160 110" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
              <rect width="160" height="110" fill="currentColor" opacity=".14"/>
              {svg}
              <path d="M0 80 L160 80 L160 110 L0 110 Z" fill="#000" opacity=".06"/>
            </svg>
            <span class="listing-tag {tag_class}">{ptype}</span>
          </div>
          <div class="lcard-body">
            <div>
              <p class="listing-addr">{prop['name']}</p>
              <p class="listing-sub">{prop.get('county_name','')}, {prop.get('state','')} · {prop.get('total_units',0)} units</p>
              <ul class="listing-meta"><li>${prop.get('avg_monthly_rent',0):,.0f}/mo</li><li>Occ {prop.get('occupied_units',0)}/{prop.get('total_units',0)}</li></ul>
            </div>
            <div class="listing-price">
              <p class="price">${prop.get('acquisition_price',0)/1e6:,.1f}<span>M</span></p>
              <p class="price-sub">{'Restricted' if prop.get('rent_restricted') else 'Market rate'}</p>
            </div>
          </div>
        </article>"""

    pipeline_rows = ""
    for rec in data["pipeline"]:
        pipeline_rows += f"""<tr>
          <td>{rec['state']}</td>
          <td>{rec['property_type']}</td>
          <td>{rec['count']}</td>
          <td>{rec['units']:,}</td>
          <td>${rec['value']:.1f}M</td>
        </tr>"""

    sim_rows = ""
    for prop in data["sim_properties"][:20]:
        dscr_val = f"{prop['dscr']:.2f}x" if prop.get('dscr') else "—"
        sim_rows += f"""<tr data-rent="{prop['current_rent']}" data-noi="{prop['current_noi']}" data-units="{prop['total_units']}">
          <td><div class="who"><span class="who-av">{prop['name'][:2].upper()}</span><div><b>{prop['name']}</b><span>{prop.get('county_name','')}, {prop['state']}</span></div></div></td>
          <td><span class="stage-pill st-{'show' if prop['property_type']=='mhp_lot' else 'offer' if prop['property_type']=='lihtc_apartment' else 'esc'}">{type_labels.get(prop['property_type'],'')}</span></td>
          <td>{prop['total_units']}</td>
          <td class="rent-cell">${prop['current_rent']:,.0f}</td>
          <td class="noi-cell">${prop['current_noi']:,.0f}</td>
          <td class="dscr-cell">{dscr_val}</td>
        </tr>"""

    today = date.today()
    weekday = today.strftime("%A")
    date_str = today.strftime("%B %d, %Y")

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Portfolio Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
{css}

/* Override: allow scroll on data-heavy tabs */
.view[data-view="market"] {{ overflow-y: auto; }}
.view[data-view="simulate"] {{ overflow-y: auto; }}

/* Simulation controls */
.sim-controls {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 16px;
}}
.sim-control {{
  background: var(--card);
  border: 1px solid var(--rule-soft);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  box-shadow: var(--shadow-card);
}}
.sim-control label {{
  display: block;
  font-family: var(--sans);
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--muted);
  margin-bottom: 6px;
}}
.sim-control input[type="range"] {{
  width: 100%;
  accent-color: var(--accent);
}}
.sim-control .sim-val {{
  font-family: var(--mono);
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--ink);
  margin-top: 4px;
}}

/* KPI summary row for simulation */
.sim-kpis {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 16px;
}}
.sim-kpi {{
  background: var(--card);
  border: 1px solid var(--rule-soft);
  border-left: 3px solid var(--accent);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  box-shadow: var(--shadow-card);
}}
.sim-kpi:nth-child(2) {{ border-left-color: var(--brass); }}
.sim-kpi:nth-child(3) {{ border-left-color: var(--slate); }}
.sim-kpi:nth-child(4) {{ border-left-color: var(--burgundy); }}
.sim-kpi .kpi-label {{ font-family: var(--sans); font-size: 0.78rem; color: var(--muted); font-weight: 500; }}
.sim-kpi .kpi-value {{ font-family: var(--serif); font-size: 1.8rem; font-weight: 500; color: var(--ink); margin: 4px 0 2px; font-variant-numeric: tabular-nums; }}
.sim-kpi .kpi-delta {{ font-family: var(--sans); font-size: 0.78rem; }}
.sim-kpi .kpi-delta.up {{ color: var(--accent); }}
.sim-kpi .kpi-delta.down {{ color: var(--burgundy); }}

.chart-container {{ min-height: 350px; }}
.plotly-chart {{ width: 100%; }}
</style>
</head>
<body>
<div class="accent-rule"></div>

<header class="topbar">
  <div class="brand">
    <svg class="brand-mark" viewBox="0 0 32 32" aria-hidden="true">
      <path d="M4 28 L4 14 L16 5 L28 14 L28 28 L20 28 L20 19 L12 19 L12 28 Z" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
      <path d="M4 14 L28 14" stroke="currentColor" stroke-width="1.4"/>
    </svg>
    <div class="brand-lockup">
      <div class="brand-name">Portfolio Analytics</div>
      <div class="brand-tag">Market intelligence · demo</div>
    </div>
  </div>
  <nav class="tabs" role="tablist">
    <button class="tab is-active" data-tab="dashboard" role="tab">Dashboard</button>
    <button class="tab" data-tab="listings" role="tab">Properties <span class="tab-badge">{p['total_properties']}</span></button>
    <button class="tab" data-tab="pipeline" role="tab">Portfolio</button>
    <button class="tab" data-tab="market" role="tab">Market</button>
    <button class="tab" data-tab="simulate" role="tab">Simulate</button>
  </nav>
  <div class="topbar-right">
    <div class="search">
      <svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="7" cy="7" r="5" fill="none" stroke="currentColor" stroke-width="1.2"/><path d="m11 11 3.5 3.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
      <input type="text" placeholder="Search properties…" aria-label="Search" />
      <span class="kbd">⌘K</span>
    </div>
    <div class="avatar" title="Demo">AI</div>
  </div>
</header>

<main class="page">

  <!-- ==================== DASHBOARD ==================== -->
  <section class="view is-active" data-view="dashboard">
    <header class="page-head">
      <div>
        <p class="kicker">{weekday} · {date_str}</p>
        <h1>Portfolio overview</h1>
        <p class="subhead">{p['total_properties']} properties · {p['total_units']:,} units · 6 states</p>
      </div>
    </header>

    <div class="kpi-row">
      <article class="kpi">
        <p class="kpi-label">Portfolio value</p>
        <p class="kpi-value">${p['total_value']}<span class="kpi-unit">M</span></p>
        <p class="kpi-delta">{p['total_properties']} properties across {len(p['states'])} states</p>
      </article>
      <article class="kpi">
        <p class="kpi-label">Total units</p>
        <p class="kpi-value">{p['total_units']:,}</p>
        <div class="kpi-bar"><span style="width:{data['portfolio']['by_type'].get('mhp_lot',0)/p['total_units']*100:.0f}%"></span></div>
        <p class="kpi-delta">{data['portfolio']['by_type'].get('mhp_lot',0):,} MHP · {data['portfolio']['by_type'].get('lihtc_apartment',0):,} LIHTC · {data['portfolio']['by_type'].get('market_apartment',0):,} Market</p>
      </article>
      <article class="kpi">
        <p class="kpi-label">Avg. monthly rent</p>
        <p class="kpi-value">${p['avg_rent']:,.0f}</p>
        <p class="kpi-delta">Across all property types</p>
      </article>
      <article class="kpi">
        <p class="kpi-label">States</p>
        <p class="kpi-value">{len(p['states'])}</p>
        <p class="kpi-delta">{', '.join(p['states'])}</p>
      </article>
    </div>

    <div class="dash-grid">
      <section class="panel">
        <header class="panel-head"><div><p class="panel-kicker">Migration pressure</p><h2>Top destinations vs. LIHTC supply</h2></div></header>
        <div id="chart-migration" class="plotly-chart"></div>
      </section>
      <aside class="side-rail">
        <section class="panel">
          <header class="panel-head tight"><div><p class="panel-kicker">Preservation</p><h2>Units expiring</h2></div></header>
          <div id="chart-preservation" class="plotly-chart"></div>
        </section>
        <section class="panel activity-panel">
          <header class="panel-head tight"><div><p class="panel-kicker">Rent burden</p><h2>Top strained counties</h2></div></header>
          <ul class="activity" style="overflow:auto">
            {''.join(f'''<li><span class="act-time" style="width:auto;min-width:40px">{r['burden_ratio']:.2f}x</span><span class="act-dot {'priority' if r['burden_ratio']>1.2 else 'warm' if r['burden_ratio']>1.0 else ''}"></span><div><p><b>{r['label']}</b></p><p class="act-sub">FMR ${r['fmr26_2']:,.0f} · VLI ${r['vli_4person']:,.0f}</p></div></li>''' for r in data['burden'][:8])}
          </ul>
        </section>
      </aside>
    </div>
  </section>

  <!-- ==================== LISTINGS ==================== -->
  <section class="view" data-view="listings">
    <header class="page-head">
      <div>
        <p class="kicker">Inventory</p>
        <h1>Portfolio properties</h1>
        <p class="subhead">{p['total_properties']} properties · {p['total_units']:,} total units · ${p['total_value']:.0f}M portfolio value</p>
      </div>
    </header>
    <div class="listings-grid">
      {listing_cards}
    </div>
  </section>

  <!-- ==================== PORTFOLIO ==================== -->
  <section class="view" data-view="pipeline">
    <header class="page-head">
      <div>
        <p class="kicker">Composition</p>
        <h1>Portfolio breakdown</h1>
        <p class="subhead">By state and property type</p>
      </div>
    </header>
    <div class="clients-wrap">
      <table class="clients-table">
        <thead><tr><th>State</th><th>Type</th><th>Properties</th><th>Units</th><th>Value</th></tr></thead>
        <tbody>{pipeline_rows}</tbody>
      </table>
    </div>
  </section>

  <!-- ==================== MARKET ==================== -->
  <section class="view" data-view="market">
    <header class="page-head">
      <div>
        <p class="kicker">Federal data · FY 2026</p>
        <h1>Market intelligence</h1>
        <p class="subhead">HUD Fair Market Rents · Income Limits · IRS Migration · LIHTC inventory</p>
      </div>
    </header>
    <div class="market-grid" style="grid-template-rows: auto auto;">
      <section class="panel chart-panel" style="grid-row: span 1;">
        <header class="panel-head tight"><div><p class="panel-kicker">FMR trajectory</p><h2>2BR Fair Market Rent — top migration counties</h2></div></header>
        <div id="chart-trajectory" class="plotly-chart"></div>
      </section>
      <section class="panel">
        <header class="panel-head tight"><div><p class="panel-kicker">Rent burden index</p><h2>FMR ÷ 30% of VLI</h2></div></header>
        <div id="chart-burden" class="plotly-chart"></div>
      </section>
    </div>
  </section>

  <!-- ==================== SIMULATE ==================== -->
  <section class="view" data-view="simulate">
    <header class="page-head">
      <div>
        <p class="kicker">What-if analysis</p>
        <h1>Rent simulation</h1>
        <p class="subhead">Adjust assumptions and see portfolio-wide impact in real time</p>
      </div>
    </header>

    <div class="sim-controls">
      <div class="sim-control">
        <label>Annual rent increase</label>
        <input type="range" id="sim-rent" min="0" max="10" step="0.5" value="3" />
        <div class="sim-val" id="sim-rent-val">3.0%</div>
      </div>
      <div class="sim-control">
        <label>Expense growth</label>
        <input type="range" id="sim-exp" min="0" max="8" step="0.5" value="2" />
        <div class="sim-val" id="sim-exp-val">2.0%</div>
      </div>
      <div class="sim-control">
        <label>Occupancy change</label>
        <input type="range" id="sim-occ" min="-10" max="5" step="1" value="0" />
        <div class="sim-val" id="sim-occ-val">0 pp</div>
      </div>
      <div class="sim-control">
        <label>Years forward</label>
        <input type="range" id="sim-yrs" min="1" max="10" step="1" value="5" />
        <div class="sim-val" id="sim-yrs-val">5</div>
      </div>
    </div>

    <div class="sim-kpis">
      <div class="sim-kpi"><p class="kpi-label">Projected NOI change</p><p class="kpi-value" id="sim-noi-delta">—</p><p class="kpi-delta" id="sim-noi-pct"></p></div>
      <div class="sim-kpi"><p class="kpi-label">Avg projected rent</p><p class="kpi-value" id="sim-avg-rent">—</p><p class="kpi-delta" id="sim-rent-note"></p></div>
      <div class="sim-kpi"><p class="kpi-label">Properties at ceiling</p><p class="kpi-value" id="sim-capped">—</p><p class="kpi-delta" id="sim-capped-note"></p></div>
      <div class="sim-kpi"><p class="kpi-label">Avg DSCR</p><p class="kpi-value" id="sim-dscr">—</p><p class="kpi-delta" id="sim-dscr-note"></p></div>
    </div>

    <div class="clients-wrap" style="max-height: 400px; overflow-y: auto;">
      <table class="clients-table" id="sim-table">
        <thead><tr><th>Property</th><th>Type</th><th>Units</th><th>Current rent</th><th>Projected NOI</th><th>DSCR</th></tr></thead>
        <tbody>{sim_rows}</tbody>
      </table>
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
    document.querySelector('[data-view="' + t.dataset.tab + '"]').classList.add('is-active');
    // Resize plotly charts when tab becomes visible
    setTimeout(() => window.dispatchEvent(new Event('resize')), 50);
  }});
}});

// Plotly config
const plotlyConfig = {{ responsive: true, displayModeBar: false }};
const layout_base = {{
  font: {{ family: 'IBM Plex Sans, sans-serif', color: '#2C3540' }},
  paper_bgcolor: '#FFFFFF',
  plot_bgcolor: '#FFFFFF',
  margin: {{ l: 160, r: 20, t: 10, b: 40 }},
  xaxis: {{ gridcolor: '#EEE9DB' }},
  yaxis: {{ gridcolor: '#EEE9DB' }},
}};

// Migration chart
const mig = DATA.migration.slice().reverse();
Plotly.newPlot('chart-migration', [
  {{ y: mig.map(r => r.label), x: mig.map(r => r.net_migration_returns), type: 'bar', orientation: 'h', name: 'Net in-migration', marker: {{ color: '#1F4A3D' }} }},
  {{ y: mig.map(r => r.label), x: mig.map(r => r.lihtc_total_units), type: 'bar', orientation: 'h', name: 'LIHTC units', marker: {{ color: '#B07A2A' }} }},
], {{ ...layout_base, barmode: 'group', height: 420, legend: {{ orientation: 'h', y: -0.08 }} }}, plotlyConfig);

// Preservation chart
const pres = DATA.preservation;
const pKeys = Object.keys(pres);
Plotly.newPlot('chart-preservation', [{{
  x: pKeys, y: pKeys.map(k => pres[k]), type: 'bar',
  marker: {{ color: ['#6B7680','#B34747','#7A4A4A','#B07A2A','#1F4A3D'] }},
}}], {{ ...layout_base, margin: {{ l: 40, r: 10, t: 10, b: 80 }}, height: 220, xaxis: {{ tickangle: -30 }}, showlegend: false }}, plotlyConfig);

// Trajectory chart
const traj = DATA.trajectory;
const counties = [...new Set(traj.map(r => r.label))];
const trajTraces = counties.map((c, i) => {{
  const pts = traj.filter(r => r.label === c && !r.projected).sort((a,b) => a.year - b.year);
  return {{ x: pts.map(r => r.year), y: pts.map(r => r.fmr_2br), mode: 'lines+markers', name: c, marker: {{ size: 4 }} }};
}});
Plotly.newPlot('chart-trajectory', trajTraces, {{
  ...layout_base, margin: {{ l: 60, r: 20, t: 10, b: 40 }}, height: 340,
  xaxis: {{ ...layout_base.xaxis, title: 'Year' }}, yaxis: {{ ...layout_base.yaxis, title: 'FMR 2BR ($)' }},
  legend: {{ font: {{ size: 9 }}, orientation: 'h', y: -0.2 }},
}}, plotlyConfig);

// Burden chart
const burden = DATA.burden.slice(0, 15).reverse();
Plotly.newPlot('chart-burden', [{{
  y: burden.map(r => r.label), x: burden.map(r => r.burden_ratio), type: 'bar', orientation: 'h',
  marker: {{ color: burden.map(r => r.burden_ratio > 1.0 ? '#B34747' : '#1F4A3D') }},
}}], {{
  ...layout_base, height: 340, showlegend: false,
  shapes: [{{ type: 'line', x0: 1.0, x1: 1.0, y0: -0.5, y1: 14.5, line: {{ color: '#333', dash: 'dash', width: 1 }} }}],
}}, plotlyConfig);

// Simulation logic
function runSim() {{
  const rentInc = parseFloat(document.getElementById('sim-rent').value);
  const expGrow = parseFloat(document.getElementById('sim-exp').value);
  const occDelta = parseFloat(document.getElementById('sim-occ').value);
  const years = parseInt(document.getElementById('sim-yrs').value);

  document.getElementById('sim-rent-val').textContent = rentInc.toFixed(1) + '%';
  document.getElementById('sim-exp-val').textContent = expGrow.toFixed(1) + '%';
  document.getElementById('sim-occ-val').textContent = occDelta + ' pp';
  document.getElementById('sim-yrs-val').textContent = years;

  let totalCurrentNOI = 0, totalProjNOI = 0, capped = 0, dscrSum = 0, dscrCount = 0;
  let totalProjRent = 0, rentCount = 0;

  document.querySelectorAll('#sim-table tbody tr').forEach(row => {{
    const curRent = parseFloat(row.dataset.rent);
    const curNOI = parseFloat(row.dataset.noi);
    const units = parseInt(row.dataset.units);

    const projRent = curRent * Math.pow(1 + rentInc/100, years);
    const projNOI = curNOI * Math.pow(1 + (rentInc - expGrow)/100, years) * (1 + occDelta/100);

    totalCurrentNOI += curNOI;
    totalProjNOI += projNOI;
    totalProjRent += projRent;
    rentCount++;

    const cells = row.querySelectorAll('td');
    cells[3].textContent = '$' + Math.round(projRent).toLocaleString();
    cells[4].textContent = '$' + Math.round(projNOI).toLocaleString();

    const dscr = projNOI / (curNOI * 0.65);
    if (!isNaN(dscr) && isFinite(dscr)) {{
      cells[5].textContent = dscr.toFixed(2) + 'x';
      dscrSum += dscr;
      dscrCount++;
    }}
  }});

  const noiDelta = totalProjNOI - totalCurrentNOI;
  const noiPct = totalCurrentNOI > 0 ? (noiDelta / totalCurrentNOI * 100) : 0;
  const sign = noiDelta >= 0 ? '+' : '';

  document.getElementById('sim-noi-delta').textContent = sign + '$' + (noiDelta/1e6).toFixed(1) + 'M';
  document.getElementById('sim-noi-pct').textContent = sign + noiPct.toFixed(1) + '% over ' + years + ' years';
  document.getElementById('sim-noi-pct').className = 'kpi-delta ' + (noiDelta >= 0 ? 'up' : 'down');

  document.getElementById('sim-avg-rent').textContent = '$' + Math.round(totalProjRent / rentCount).toLocaleString();
  document.getElementById('sim-rent-note').textContent = 'from $' + Math.round(DATA.portfolio.avg_rent).toLocaleString() + ' current';

  document.getElementById('sim-dscr').textContent = dscrCount > 0 ? (dscrSum/dscrCount).toFixed(2) + 'x' : '—';
}}

['sim-rent','sim-exp','sim-occ','sim-yrs'].forEach(id => {{
  document.getElementById(id).addEventListener('input', runSim);
}});
runSim();
</script>
</body>
</html>"""

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html)
    print(f"Dashboard written to: {OUT_PATH}")
    print(f"Size: {OUT_PATH.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
