import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="Market Analytics Dashboard")


@app.cell
def _():
    import marimo as mo
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.io as pio
    import folium
    from folium.plugins import MarkerCluster
    import pandas as pd
    import numpy as np

    import dashboard_data as dd

    COLORS = {
        "teal": "#0F5F4D",
        "gold": "#B07A2A",
        "navy": "#3F4F75",
        "burgundy": "#7A4A4A",
        "red": "#B34747",
        "bg": "#f8f7f5",
        "card": "#ffffff",
        "text": "#2c3540",
        "muted": "#6b7280",
    }

    pio.templates["editorial"] = go.layout.Template(
        layout=go.Layout(
            font=dict(family="IBM Plex Sans, sans-serif", color=COLORS["text"]),
            paper_bgcolor=COLORS["card"],
            plot_bgcolor=COLORS["card"],
            title=dict(font=dict(size=14, family="IBM Plex Sans, sans-serif")),
            xaxis=dict(gridcolor="#e5e5e0", gridwidth=1),
            yaxis=dict(gridcolor="#e5e5e0", gridwidth=1),
        )
    )
    pio.templates.default = "editorial"

    return COLORS, MarkerCluster, dd, folium, go, mo, np, pd, pio, px


@app.cell
def _(mo):
    mo.Html("""<style>
        body { background: #f8f7f5 !important; }
        .marimo-output { font-family: 'IBM Plex Serif', Georgia, serif !important; }
        h1, h2, h3 { font-family: 'IBM Plex Sans', sans-serif !important; }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Serif:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet" />
    """)
    return


@app.cell
def _(mo, dd):
    mo.md(f"""
    # Market Analytics Dashboard
    *AI-assembled market view from public federal data · {dd.TARGET_STATE_NAME} focus*

    Five views built from HUD LIHTC, HUD Fair Market Rents, HUD Income Limits,
    and IRS county-to-county migration data. Sliders let you run simple
    projections — what happens if rents grow faster, or a share of expiring
    subsidies convert to market rate.
    """)
    return


@app.cell
def _(mo):
    mo.md("## 1. Property Map")
    return


@app.cell
def _(dd, folium, MarkerCluster, COLORS, mo):
    map_df = dd.prepare_map_data()

    status_colors = {
        "Active (10yr+)": COLORS["teal"],
        "Expiring 5–10yr": COLORS["gold"],
        "Expiring ≤5yr": COLORS["red"],
        "Expired": COLORS["muted"],
        "Unknown": "#999999",
    }

    center_lat = map_df["latitude"].mean()
    center_lon = map_df["longitude"].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6,
                   tiles="cartodbpositron")
    cluster = MarkerCluster(name="LIHTC Projects").add_to(m)

    for _, row in map_df.iterrows():
        color = status_colors.get(row["status"], "#999")
        popup = (
            f"<b>{row['project']}</b><br>"
            f"{row['proj_cty']}<br>"
            f"Units: {row['n_units']}<br>"
            f"Placed in service: {int(row['yr_pis']) if pd.notna(row['yr_pis']) else '?'}<br>"
            f"Expiration: {int(row['expiration_year']) if pd.notna(row['expiration_year']) else '?'}<br>"
            f"Status: {row['status']}"
        )
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=4, color=color, fill=True, fill_color=color,
            fill_opacity=0.7, popup=popup,
        ).add_to(cluster)

    import pandas as _pd
    legend_html = "<br>".join(
        f'<span style="color:{c}">●</span> {s}'
        for s, c in status_colors.items()
    )
    mo.vstack([
        mo.Html(m._repr_html_()),
        mo.md(f"**{len(map_df):,}** projects mapped · Legend: {legend_html}"),
    ])
    return map_df,


@app.cell
def _(mo):
    mo.md("---\n## 2. Migration vs. Subsidized Supply")
    return


@app.cell
def _(mo):
    mig_top_n = mo.ui.slider(10, 50, value=25, step=5, label="Show top N counties")
    mig_top_n
    return (mig_top_n,)


@app.cell
def _(dd, px, COLORS, mig_top_n):
    mig_df = dd.prepare_migration_data(top_n=mig_top_n.value)
    mig_df = mig_df.sort_values("net_migration_returns", ascending=True)

    fig_mig = go.Figure()
    fig_mig.add_trace(go.Bar(
        y=mig_df["label"], x=mig_df["net_migration_returns"],
        orientation="h", name="Net in-migration (HH)",
        marker_color=COLORS["teal"],
    ))
    fig_mig.add_trace(go.Bar(
        y=mig_df["label"], x=mig_df["lihtc_total_units"],
        orientation="h", name="LIHTC units (cumulative)",
        marker_color=COLORS["gold"],
    ))
    fig_mig.update_layout(
        barmode="group", height=max(400, len(mig_df) * 28),
        title="Net IRS in-migration (FY 2022–23) vs. cumulative LIHTC units",
        xaxis_title="Households / units",
        legend=dict(orientation="h", y=-0.05),
        margin=dict(l=200),
    )
    fig_mig
    return (fig_mig,)


@app.cell
def _(mo):
    mo.md(f"---\n## 3. Rent Burden + Projection")
    return


@app.cell
def _(mo):
    burden_growth = mo.ui.slider(0, 8, value=3, step=0.5, label="Annual FMR growth rate (%)")
    burden_years = mo.ui.slider(1, 10, value=5, step=1, label="Projection years")
    mo.hstack([burden_growth, burden_years])
    return burden_growth, burden_years


@app.cell
def _(dd, go, COLORS, burden_growth, burden_years, pd, mo):
    bdf = dd.prepare_burden_data().head(30)
    _burden_proj = dd.project_burden(bdf, burden_growth.value, burden_years.value)

    target_year = 2026 + burden_years.value
    proj_at_target = _burden_proj[_burden_proj["year"] == target_year].sort_values("projected_ratio", ascending=False).head(30)

    fig_burden = go.Figure()
    fig_burden.add_trace(go.Bar(
        y=bdf.sort_values("burden_ratio", ascending=True)["label"],
        x=bdf.sort_values("burden_ratio", ascending=True)["burden_ratio"],
        orientation="h", name="FY 2026 (actual)",
        marker_color=[COLORS["red"] if r > 1 else COLORS["teal"] for r in bdf.sort_values("burden_ratio", ascending=True)["burden_ratio"]],
    ))

    fig_burden.add_vline(x=1.0, line_dash="dash", line_color="#333",
                         annotation_text="Affordability threshold")
    fig_burden.update_layout(
        height=max(400, len(bdf) * 24),
        title=f"Rent burden ratio — FMR 2BR ÷ 30% of VLI monthly (FY 2026)",
        xaxis_title="Burden ratio (>1.0 = unaffordable)",
        margin=dict(l=200),
    )

    flipped = proj_at_target[proj_at_target["projected_ratio"] > 1.0]
    currently_above = (bdf["burden_ratio"] > 1.0).sum()
    projected_above = len(flipped)

    mo.vstack([
        fig_burden,
        mo.md(f"**Projection at {burden_growth.value}% annual FMR growth:**  "
              f"By {target_year}, **{projected_above}** of the top 30 counties "
              f"would have a burden ratio > 1.0 (currently {currently_above})."),
    ])
    return


@app.cell
def _(mo):
    mo.md("---\n## 4. Preservation Pipeline")
    return


@app.cell
def _(mo):
    conversion_pct = mo.ui.slider(0, 100, value=25, step=5, label="Estimated market-rate conversion (%)")
    conversion_pct
    return (conversion_pct,)


@app.cell
def _(dd, go, px, COLORS, conversion_pct, mo):
    pres_df = dd.prepare_preservation_data()
    bucket_order = ["Already expired", f"{dd.CURRENT_YEAR}–{dd.CURRENT_YEAR+3}",
                    f"{dd.CURRENT_YEAR+4}–{dd.CURRENT_YEAR+5}",
                    f"{dd.CURRENT_YEAR+6}–{dd.CURRENT_YEAR+10}",
                    f"After {dd.CURRENT_YEAR+10}"]

    by_bucket = pres_df.groupby("bucket")["n_units"].sum().reindex(bucket_order).fillna(0)

    fig_pres = go.Figure()
    bar_colors = [COLORS["muted"], COLORS["red"], COLORS["burgundy"],
                  COLORS["gold"], COLORS["teal"]]
    fig_pres.add_trace(go.Bar(
        x=by_bucket.index, y=by_bucket.values,
        marker_color=bar_colors[:len(by_bucket)],
    ))
    fig_pres.update_layout(
        title=f"LIHTC units by affordability expiration bucket — {dd.TARGET_STATE_NAME}",
        yaxis_title="Units",
        height=400,
    )

    _pres_at_risk = pres_df[pres_df["bucket"].isin(bucket_order[:4])]["n_units"].sum()
    units_lost = int(_pres_at_risk * conversion_pct.value / 100)

    mo.vstack([
        fig_pres,
        mo.callout(
            mo.md(f"If **{conversion_pct.value}%** of projects expiring through "
                  f"{dd.CURRENT_YEAR+10} convert to market rate: "
                  f"**{units_lost:,} affordable units lost** "
                  f"(out of {int(_pres_at_risk):,} at risk)."),
            kind="warn",
        ),
    ])
    return


@app.cell
def _(mo):
    mo.md("---\n## 5. Rent Trajectory + Projection")
    return


@app.cell
def _(mo):
    traj_growth = mo.ui.slider(0, 8, value=3, step=0.5, label="FMR growth rate (%/yr)")
    traj_growth
    return (traj_growth,)


@app.cell
def _(dd, go, COLORS, traj_growth, mo):
    traj_base = dd.prepare_trajectory_data(top_n=10)
    traj_all = dd.project_trajectory(traj_base, traj_growth.value, projection_years=10)

    fig_traj = go.Figure()
    for label in traj_all["label"].unique():
        subset = traj_all[traj_all["label"] == label].sort_values("year")
        actual = subset[~subset["projected"]]
        _proj_subset = subset[subset["projected"]]
        fig_traj.add_trace(go.Scatter(
            x=actual["year"], y=actual["fmr_2br"], mode="lines+markers",
            name=label, legendgroup=label, marker=dict(size=5),
        ))
        if not _proj_subset.empty:
            bridge = pd.concat([actual.tail(1), _proj_subset])
            fig_traj.add_trace(go.Scatter(
                x=bridge["year"], y=bridge["fmr_2br"], mode="lines",
                name=f"{label} (proj)", legendgroup=label,
                line=dict(dash="dot"), showlegend=False,
            ))

    fig_traj.add_vline(x=2026, line_dash="dash", line_color="#aaa",
                       annotation_text="Today")
    fig_traj.update_layout(
        title=f"2BR Fair Market Rent — top migration counties in {dd.TARGET_STATE_NAME}",
        xaxis_title="Year", yaxis_title="FMR ($)",
        height=500,
        legend=dict(font=dict(size=9)),
    )

    mo.vstack([
        fig_traj,
        mo.md(f"*Dashed lines show projection at {traj_growth.value}% annual growth from 2026.*"),
    ])
    return


@app.cell
def _(mo):
    mo.md("---\n## 6. Portfolio Rent Simulator")
    return


@app.cell
def _(mo):
    mo.md("""
    *This section uses a dummy portfolio of ~270 properties across 6 states to
    demonstrate what a rent-simulation tool would look like against your actual
    data. The rent ceilings are computed from real HUD AMI limits for each
    county — so the "hitting the ceiling" math is realistic even though the
    properties are fictional.*
    """)
    return


@app.cell
def _(mo):
    sim_rent_inc = mo.ui.slider(0, 10, value=3, step=0.5, label="Annual rent increase (%)")
    sim_expense = mo.ui.slider(0, 8, value=2, step=0.5, label="Annual expense growth (%)")
    sim_occ_delta = mo.ui.slider(-10, 5, value=0, step=1, label="Occupancy change (pp)")
    sim_years = mo.ui.slider(1, 10, value=5, step=1, label="Projection horizon (years)")
    mo.vstack([
        mo.hstack([sim_rent_inc, sim_expense]),
        mo.hstack([sim_occ_delta, sim_years]),
    ])
    return sim_rent_inc, sim_expense, sim_occ_delta, sim_years


@app.cell
def _(dd, go, px, COLORS, sim_rent_inc, sim_expense, sim_occ_delta, sim_years, mo):
    sim = dd.simulate_rent_change(
        rent_increase_pct=sim_rent_inc.value,
        expense_growth_pct=sim_expense.value,
        occupancy_delta_pct=sim_occ_delta.value,
        years=sim_years.value,
    )

    total_current_noi = sim["current_noi"].sum()
    total_proj_noi = sim["projected_noi"].sum()
    noi_delta = total_proj_noi - total_current_noi
    capped_count = sim["rent_capped"].sum()
    total_props = len(sim)
    avg_dscr = sim["dscr"].dropna().mean()
    _sim_at_risk = sim[sim["dscr"].notna() & (sim["dscr"] < 1.1)]

    fig_sim_scatter = px.scatter(
        sim, x="projected_noi", y="noi_change_pct",
        color="property_type", size="total_units",
        hover_name="name",
        hover_data={"state": True, "current_rent": ":$,.0f", "projected_rent": ":$,.0f",
                    "rent_capped": True, "dscr": ":.2f"},
        color_discrete_map={
            "mhp_lot": COLORS["teal"],
            "lihtc_apartment": COLORS["gold"],
            "market_apartment": COLORS["navy"],
        },
        labels={"projected_noi": "Projected NOI ($)", "noi_change_pct": "NOI change (%)",
                "property_type": "Type", "total_units": "Units"},
    )
    fig_sim_scatter.update_layout(
        title=f"Portfolio rent simulation — {sim_years.value}-year projection",
        height=500,
    )

    by_state = sim.groupby("state").agg(
        properties=("property_id", "count"),
        total_units=("total_units", "sum"),
        current_noi=("current_noi", "sum"),
        projected_noi=("projected_noi", "sum"),
        capped=("rent_capped", "sum"),
    ).reset_index()
    by_state["noi_change"] = by_state["projected_noi"] - by_state["current_noi"]

    fig_state = go.Figure()
    fig_state.add_trace(go.Bar(
        x=by_state["state"], y=by_state["current_noi"] / 1e6,
        name="Current NOI", marker_color=COLORS["teal"],
    ))
    fig_state.add_trace(go.Bar(
        x=by_state["state"], y=by_state["projected_noi"] / 1e6,
        name=f"Projected NOI ({sim_years.value}yr)", marker_color=COLORS["gold"],
    ))
    fig_state.update_layout(
        barmode="group", title="NOI by state — current vs. projected",
        yaxis_title="NOI ($M)", height=400,
    )

    noi_sign = "+" if noi_delta >= 0 else ""
    capped_pct = capped_count / total_props * 100 if total_props > 0 else 0

    mo.vstack([
        mo.hstack([
            mo.stat(label="Portfolio NOI change",
                    value=f"{noi_sign}${noi_delta/1e6:,.1f}M",
                    caption=f"{noi_sign}{noi_delta/total_current_noi*100:.1f}% over {sim_years.value} years" if total_current_noi else ""),
            mo.stat(label="Properties hitting AMI ceiling",
                    value=f"{capped_count} of {total_props}",
                    caption=f"{capped_pct:.0f}% of portfolio"),
            mo.stat(label="Average DSCR",
                    value=f"{avg_dscr:.2f}x" if avg_dscr else "N/A",
                    caption=f"{len(_sim_at_risk)} properties below 1.1x"),
        ]),
        fig_sim_scatter,
        fig_state,
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ---
    <p style="text-align: center; color: #6b7280; font-size: 0.85rem;">
    Built from HUD LIHTC · HUD Fair Market Rents · HUD Income Limits · IRS SOI Migration Data · Dummy portfolio data<br>
    <code style="font-size: 0.75rem; background: #f0f0ec; padding: 2px 6px; border-radius: 3px;">
    AI-generated analysis</code>
    </p>
    """)
    return


if __name__ == "__main__":
    app.run()
