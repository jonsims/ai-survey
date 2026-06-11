"""Phase 1 story — Migration vs. subsidized housing supply.

For each county, plot net IRS in-migration (FY 2022–23) against the existing
LIHTC unit count. Highlight counties where the gap between migration pressure
and existing affordable supply is most striking.

Run:    python 01_migration_vs_subsidized_supply.py
Output: output/01_migration_vs_subsidized_supply.{md,png}
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from lib import (
    county_name_map,
    lihtc_units_by_county,
    net_migration_by_county,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
SLUG = "01_migration_vs_subsidized_supply"


def build_dataset() -> pd.DataFrame:
    lihtc = lihtc_units_by_county()
    migration = net_migration_by_county()
    names = county_name_map()

    df = migration.merge(lihtc, on="fips_county", how="left")
    df[["lihtc_projects", "lihtc_total_units", "lihtc_low_income_units"]] = (
        df[["lihtc_projects", "lihtc_total_units", "lihtc_low_income_units"]].fillna(0)
    )
    df = df.merge(names, on="fips_county", how="left")
    df["label"] = df["county_name"].fillna(df["fips_county"]) + ", " + df["state"].fillna("")
    df["label"] = df["label"].str.replace(", $", "", regex=True)
    return df


def render_chart(df: pd.DataFrame, top_n: int = 25) -> Path:
    top = df.nlargest(top_n, "net_migration_returns").copy()
    top = top.sort_values("net_migration_returns", ascending=True)

    fig, ax = plt.subplots(figsize=(11, 9))
    y = range(len(top))
    bar_h = 0.4
    ax.barh([i + bar_h / 2 for i in y], top["net_migration_returns"], height=bar_h,
            color="#0F5F4D", label="Net in-migration (households)")
    ax.barh([i - bar_h / 2 for i in y], top["lihtc_total_units"], height=bar_h,
            color="#B07A2A", label="LIHTC units (cumulative, 1987–2023)")
    ax.set_yticks(list(y))
    ax.set_yticklabels(top["label"])
    ax.set_xlabel("Households / units")
    ax.set_title(
        f"Top {top_n} U.S. counties by net IRS in-migration (FY 2022–23)\n"
        "compared with their cumulative LIHTC unit count",
        loc="left",
        fontsize=12,
    )
    ax.legend(loc="lower right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    fig.tight_layout()

    out = OUTPUT_DIR / f"{SLUG}.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return out


def render_markdown(df: pd.DataFrame, chart_path: Path, top_n: int = 25) -> Path:
    top = df.nlargest(top_n, "net_migration_returns").copy()
    top["ratio_lihtc_per_inmig_hh"] = (
        top["lihtc_total_units"] / top["net_migration_returns"].replace(0, pd.NA)
    )

    top5_label = ", ".join(top.head(5)["label"].tolist())
    biggest_gap = top.loc[top["ratio_lihtc_per_inmig_hh"].idxmin()]
    biggest_buffer = top.loc[top["ratio_lihtc_per_inmig_hh"].idxmax()]

    md_path = OUTPUT_DIR / f"{SLUG}.md"
    table = top[
        ["label", "net_migration_returns", "lihtc_total_units", "lihtc_projects", "ratio_lihtc_per_inmig_hh"]
    ].rename(columns={
        "label": "County",
        "net_migration_returns": "Net in-mig HH",
        "lihtc_total_units": "LIHTC units",
        "lihtc_projects": "LIHTC projects",
        "ratio_lihtc_per_inmig_hh": "LIHTC / in-mig HH",
    })
    table["LIHTC / in-mig HH"] = table["LIHTC / in-mig HH"].round(2)
    table["Net in-mig HH"] = table["Net in-mig HH"].astype(int)
    table["LIHTC units"] = table["LIHTC units"].astype(int)
    table["LIHTC projects"] = table["LIHTC projects"].astype(int)

    md_path.write_text(f"""# Migration vs. subsidized housing supply

**Phase 1 demo · {pd.Timestamp.today().strftime("%Y-%m-%d")}**

For each U.S. county, this view compares the net household-level migration the
county absorbed during IRS Filing Year 2022–23 against the cumulative count of
Low-Income Housing Tax Credit (LIHTC) units placed in service there from 1987
through 2023. Net migration is the difference between households that filed
from the county in the current year versus a different county the year prior
(inflow) and households that did the reverse (outflow).

The top {top_n} counties by net in-migration are below. The right-hand column
is a rough "supply-per-newcomer" ratio: LIHTC units divided by net in-migrating
households. A low ratio means the affordable-housing supply has not kept pace
with population growth; a high ratio means there's existing capacity to absorb
new arrivals into the regulated stock.

The five largest migration destinations are **{top5_label}**. The widest gap
between migration pressure and existing LIHTC supply in this cohort is
**{biggest_gap['label']}** — {int(biggest_gap['net_migration_returns']):,} net
in-migrating households against {int(biggest_gap['lihtc_total_units']):,} LIHTC
units (ratio {biggest_gap['ratio_lihtc_per_inmig_hh']:.2f}). The most-buffered
county in this cohort is **{biggest_buffer['label']}**, with a ratio of
{biggest_buffer['ratio_lihtc_per_inmig_hh']:.2f}.

![Chart]({chart_path.name})

## Top {top_n} counties by net in-migration

{table.to_markdown(index=False)}

## Sources

- HUD LIHTC Database (placed in service 1987–2023; April 2025 release)
- IRS SOI county-to-county migration data, filing years 2022–2023

## Caveats

- LIHTC unit counts are cumulative since 1987 and include projects whose initial
  15-year compliance period has expired; counts overstate currently rent-restricted
  supply where the project has converted to market-rate.
- IRS migration data captures filers only; it underweights low-income, undocumented,
  and non-filing households, which are exactly the populations most relevant to
  affordable-housing demand. Treat as a directional signal, not a precise demand
  measure.
- This is a national view, not a single-state view. The top destinations are
  dominated by very large metros where both numerators are large in absolute
  terms but small per capita.
""")
    return md_path


def main():
    df = build_dataset()
    chart = render_chart(df)
    md = render_markdown(df, chart)
    print(f"Wrote:\n  {md}\n  {chart}")
    print(f"\nTotal counties analyzed: {len(df):,}")
    print(f"Counties with both migration AND LIHTC data: {(df['lihtc_total_units'] > 0).sum():,}")


if __name__ == "__main__":
    main()
