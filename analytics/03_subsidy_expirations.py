"""Story 3 — Subsidy expirations: the preservation pipeline.

Flag LIHTC projects in the target state whose initial affordability period
expires in the next 5 or 10 years. These are the properties most likely to
convert to market rate — and thus the primary targets for a preservation
acquisition strategy.

Run:    python 03_subsidy_expirations.py
Output: output/03_subsidy_expirations.{md,png}
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from lib import (
    TARGET_STATE_FIPS,
    TARGET_STATE_NAME,
    county_name_map,
    load_lihtc,
    filter_to_state,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
SLUG = "03_subsidy_expirations"
CURRENT_YEAR = 2026


def build_dataset() -> pd.DataFrame:
    df = load_lihtc()
    df = df[df["fips_county"].notna()]
    df = filter_to_state(df, "fips_county")

    df["yr_pis"] = pd.to_numeric(df["yr_pis"], errors="coerce")
    df["aff_yrs"] = pd.to_numeric(df["aff_yrs"], errors="coerce")
    df = df[df["yr_pis"].notna() & (df["yr_pis"] < 9000)].copy()

    # aff_yrs is null for ~97% of records; the statutory default is 30 years
    # (15-year initial compliance + 15-year extended use).
    df["aff_yrs_used"] = df["aff_yrs"].fillna(30)
    df["expiration_year"] = df["yr_pis"] + df["aff_yrs_used"]

    df["expires_within_5"] = (df["expiration_year"] >= CURRENT_YEAR) & (df["expiration_year"] <= CURRENT_YEAR + 5)
    df["expires_within_10"] = (df["expiration_year"] >= CURRENT_YEAR) & (df["expiration_year"] <= CURRENT_YEAR + 10)
    df["already_expired"] = df["expiration_year"] < CURRENT_YEAR

    names = county_name_map()
    df = df.merge(names, on="fips_county", how="left")
    df["label"] = df["county_name"].fillna(df["fips_county"]) + ", " + df["state"].fillna("")

    return df


def render_chart(df: pd.DataFrame, top_n: int = 20) -> Path:
    by_county = df[df["expires_within_10"]].groupby("label").agg(
        units_expiring=("n_units", "sum"),
        projects_expiring=("hud_id", "count"),
    ).reset_index().sort_values("units_expiring", ascending=False)

    top = by_county.head(top_n).sort_values("units_expiring", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(top["label"], top["units_expiring"], color="#B34747")
    ax.set_xlabel("LIHTC units with affordability expiring (2026–2036)")
    ax.set_title(
        f"Preservation pipeline — {TARGET_STATE_NAME} counties\n"
        f"LIHTC units whose initial affordability period expires within 10 years",
        loc="left", fontsize=11,
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    fig.tight_layout()

    out = OUTPUT_DIR / f"{SLUG}.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return out


def render_markdown(df: pd.DataFrame, chart_path: Path) -> Path:
    total_units = df["n_units"].sum()
    exp5 = df[df["expires_within_5"]]["n_units"].sum()
    exp10 = df[df["expires_within_10"]]["n_units"].sum()
    already = df[df["already_expired"]]["n_units"].sum()

    by_county_10 = df[df["expires_within_10"]].groupby("label").agg(
        units_expiring=("n_units", "sum"),
        projects_expiring=("hud_id", "count"),
    ).reset_index().sort_values("units_expiring", ascending=False)

    table = by_county_10.head(20).copy()
    table.columns = ["County", "Units expiring", "Projects expiring"]

    md_path = OUTPUT_DIR / f"{SLUG}.md"
    md_path.write_text(f"""# Subsidy expirations: the preservation pipeline

**{TARGET_STATE_NAME} · as of {CURRENT_YEAR}**

Every LIHTC project has a recorded affordability period — typically 15 or 30
years from when it was placed in service. Once that period expires, the owner
is no longer required to maintain below-market rents. Projects approaching
expiration are the primary pipeline for preservation acquisitions: buy them,
re-syndicate or restructure, and lock in another 30 years of affordability.

Of **{total_units:,}** total LIHTC units in {TARGET_STATE_NAME} with computable
expirations:

- **{exp5:,}** units expire within 5 years ({CURRENT_YEAR}–{CURRENT_YEAR + 5})
- **{exp10:,}** units expire within 10 years ({CURRENT_YEAR}–{CURRENT_YEAR + 10})
- **{already:,}** units have *already* passed their initial affordability period

The chart and table below show which counties have the deepest near-term
preservation pipeline.

![Chart]({chart_path.name})

## Top 20 counties by units expiring within 10 years

{table.to_markdown(index=False)}

## Sources

- HUD LIHTC Database (1987–2023; `yr_pis` + `aff_yrs` = expiration year)

## Caveats

- Many projects extend beyond the initial affordability period via extended-use
  agreements, re-syndication, or other regulatory mechanisms. An "expired"
  affordability period does not necessarily mean the project has converted to
  market-rate — but it means it *can*.
- Projects with missing `yr_pis` or `aff_yrs` are excluded from this analysis.
""")
    return md_path


def main():
    df = build_dataset()
    chart = render_chart(df)
    md = render_markdown(df, chart)
    print(f"Wrote:\n  {md}\n  {chart}")
    print(f"\n{TARGET_STATE_NAME} LIHTC projects with computable expirations: {len(df):,}")
    print(f"Units expiring within 10 years: {df[df['expires_within_10']]['n_units'].sum():,}")


if __name__ == "__main__":
    main()
