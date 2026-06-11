"""Story 4 — 40-year rent trajectory for top migration destinations.

Plot the 2-bedroom Fair Market Rent from 1990 through 2026 for the top
in-migration counties in the target state. Migration story meets price story:
are the places people are moving to also seeing the fastest rent growth?

Run:    python 04_fmr_trajectory.py
Output: output/04_fmr_trajectory.{md,png}
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from lib import (
    TARGET_STATE_NAME,
    county_name_map,
    filter_to_state,
    load_fmr_history,
    net_migration_by_county,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
SLUG = "04_fmr_trajectory"

YEAR_COLS = [
    ("fmr90_2", 1990), ("fmr95_2", 1995), ("fmr00_2", 2000),
    ("fmr05_2", 2005), ("fmr10_2", 2010), ("fmr15_2", 2015),
    ("fmr20_2", 2020), ("fmr26_2", 2026),
]


def build_dataset(top_n: int = 10) -> tuple[pd.DataFrame, pd.DataFrame]:
    migration = net_migration_by_county()
    migration = filter_to_state(migration, "fips_county")
    top_counties = migration.nlargest(top_n, "net_migration_returns")["fips_county"].tolist()

    fmr = load_fmr_history()
    fmr["fips_county"] = fmr["fips"].str.zfill(10).str[:5]
    fmr = filter_to_state(fmr, "fips_county")
    fmr = fmr[fmr["cousub"].fillna("99999") == "99999"]
    fmr = fmr[fmr["fips_county"].isin(top_counties)]

    names = county_name_map()
    fmr = fmr.merge(names, on="fips_county", how="left")
    fmr["label"] = fmr["county_name"].fillna(fmr["fips_county"])

    for col, _ in YEAR_COLS:
        if col in fmr.columns:
            fmr[col] = pd.to_numeric(fmr[col], errors="coerce")

    return fmr, migration[migration["fips_county"].isin(top_counties)]


def render_chart(fmr: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(11, 7))
    available = [(c, y) for c, y in YEAR_COLS if c in fmr.columns]

    for _, row in fmr.iterrows():
        years = [y for c, y in available if pd.notna(row.get(c))]
        rents = [row[c] for c, y in available if pd.notna(row.get(c))]
        if years:
            ax.plot(years, rents, marker="o", markersize=4, linewidth=1.8, label=row["label"])

    ax.set_xlabel("Fiscal year")
    ax.set_ylabel("2-bedroom Fair Market Rent ($)")
    ax.set_title(
        f"2BR Fair Market Rent trajectory — top migration destinations in {TARGET_STATE_NAME}\n"
        "FY 1990 – FY 2026 (5-year intervals)",
        loc="left", fontsize=11,
    )
    ax.legend(fontsize=8, loc="upper left", frameon=False, ncol=2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()

    out = OUTPUT_DIR / f"{SLUG}.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return out


def render_markdown(fmr: pd.DataFrame, chart_path: Path) -> Path:
    available = [(c, y) for c, y in YEAR_COLS if c in fmr.columns]
    first_yr_col = available[0][0] if available else None
    last_yr_col = available[-1][0] if available else None

    rows = []
    for _, r in fmr.iterrows():
        start = r.get(first_yr_col)
        end = r.get(last_yr_col)
        if pd.notna(start) and pd.notna(end) and start > 0:
            growth = (end - start) / start * 100
            rows.append({"County": r["label"], f"FMR {available[0][1]}": f"${start:,.0f}",
                         f"FMR {available[-1][1]}": f"${end:,.0f}", "Growth (%)": f"{growth:.0f}%"})

    table = pd.DataFrame(rows)
    fastest = table.iloc[0]["County"] if not table.empty else "N/A"

    md_path = OUTPUT_DIR / f"{SLUG}.md"
    md_path.write_text(f"""# Rent trajectory: are destination markets getting more expensive?

**{TARGET_STATE_NAME} · FY 1990–2026**

This chart tracks the 2-bedroom Fair Market Rent over ~35 years for the
{TARGET_STATE_NAME} counties absorbing the most net in-migration (per IRS data,
FY 2022–23). The question it answers: are the places people are moving to
*also* the places where rents are climbing fastest?

![Chart]({chart_path.name})

## Growth summary

{table.to_markdown(index=False) if not table.empty else "No data available."}

## Sources

- HUD Fair Market Rents (all bedroom sizes, 1983–2026)
- IRS SOI county-to-county migration data, filing years 2022–2023

## Interpretation

FMR growth reflects HUD's estimate of what *modest* rental units cost, not
luxury or median rent. Where FMR growth outpaces income growth, the
affordable-housing gap widens even before considering population pressure
from in-migration.
""")
    return md_path


def main():
    fmr, _ = build_dataset()
    chart = render_chart(fmr)
    md = render_markdown(fmr, chart)
    print(f"Wrote:\n  {md}\n  {chart}")
    print(f"\nCounties plotted: {len(fmr)}")


if __name__ == "__main__":
    main()
