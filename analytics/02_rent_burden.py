"""Story 2 — Rent burden: where FMR exceeds what VLI households can afford.

For each county in the target state, compute whether the HUD-set Fair Market
Rent (2BR) exceeds 30% of the Very Low Income limit (50% AMI, 4-person HH).
When it does, the program's own rent benchmark is unaffordable to the people
the program is designed to serve.

Run:    python 02_rent_burden.py
Output: output/02_rent_burden.{md,png}
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from lib import (
    TARGET_STATE_NAME,
    fmr_2br_county,
    income_limits_county,
    filter_to_state,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
SLUG = "02_rent_burden"


def build_dataset() -> pd.DataFrame:
    fmr = fmr_2br_county()
    il = income_limits_county()

    df = fmr.merge(il, on="fips_county", how="inner")
    df = filter_to_state(df, "fips_county")

    df["fmr26_2"] = pd.to_numeric(df["fmr26_2"], errors="coerce")
    df["vli_4person"] = pd.to_numeric(df["vli_4person"], errors="coerce")

    df["monthly_30pct_vli"] = df["vli_4person"] / 12 * 0.30
    df["burden_ratio"] = df["fmr26_2"] / df["monthly_30pct_vli"]
    df["label"] = df["county_name"].fillna(df["fips_county"])

    return df.dropna(subset=["burden_ratio"]).sort_values("burden_ratio", ascending=False)


def render_chart(df: pd.DataFrame, top_n: int = 25) -> Path:
    top = df.head(top_n).copy().sort_values("burden_ratio", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 9))
    colors = ["#B34747" if r > 1.0 else "#0F5F4D" for r in top["burden_ratio"]]
    ax.barh(top["label"], top["burden_ratio"], color=colors)
    ax.axvline(x=1.0, color="#333", linestyle="--", linewidth=0.8, label="Affordability threshold (30% of VLI)")
    ax.set_xlabel("FMR 2BR ÷ 30% of VLI monthly income")
    ax.set_title(
        f"Rent burden index — {TARGET_STATE_NAME} counties (FY 2026)\n"
        "Ratio > 1.0 means the HUD Fair Market Rent exceeds 30% of Very Low Income",
        loc="left", fontsize=11,
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
    top = df.head(top_n).copy()
    burdened = (top["burden_ratio"] > 1.0).sum()
    worst = top.iloc[0]

    table = top[["label", "fmr26_2", "vli_4person", "monthly_30pct_vli", "burden_ratio"]].copy()
    table.columns = ["County", "FMR 2BR", "VLI (annual)", "30% VLI (monthly)", "Burden ratio"]
    table["FMR 2BR"] = table["FMR 2BR"].apply(lambda x: f"${x:,.0f}")
    table["VLI (annual)"] = table["VLI (annual)"].apply(lambda x: f"${x:,.0f}")
    table["30% VLI (monthly)"] = table["30% VLI (monthly)"].apply(lambda x: f"${x:,.0f}")
    table["Burden ratio"] = table["Burden ratio"].round(2)

    md_path = OUTPUT_DIR / f"{SLUG}.md"
    md_path.write_text(f"""# Rent burden: where "affordable" still isn't

**{TARGET_STATE_NAME} · FY 2026**

HUD's Fair Market Rent is meant to represent what a modest rental unit costs in
a given market. The Very Low Income limit (50% of Area Median Income) defines
who qualifies for the deepest subsidies. When FMR exceeds 30% of a VLI
household's monthly income, the program's own benchmark rent is unaffordable
to the population it targets — a structural gap, not a personal one.

Of the top {top_n} {TARGET_STATE_NAME} counties shown, **{burdened}** have a
burden ratio above 1.0 — meaning FMR exceeds the 30%-of-income threshold for
a 4-person VLI household. The most strained is **{worst['label']}** at
{worst['burden_ratio']:.2f}x.

![Chart]({chart_path.name})

## Top {top_n} counties by rent burden ratio

{table.to_markdown(index=False)}

## Sources

- HUD FY 2026 Fair Market Rents (revised)
- HUD FY 2026 Section 8 Income Limits

## Interpretation note

A burden ratio below 1.0 does not mean affordable housing is plentiful — it
means the FMR is *mathematically* within reach for VLI households. Whether
units are actually *available* at FMR is a separate question this data does
not answer.
""")
    return md_path


def main():
    df = build_dataset()
    chart = render_chart(df)
    md = render_markdown(df, chart)
    print(f"Wrote:\n  {md}\n  {chart}")
    print(f"\n{TARGET_STATE_NAME} counties analyzed: {len(df)}")
    burdened = (df["burden_ratio"] > 1.0).sum()
    print(f"Counties with burden ratio > 1.0: {burdened}")


if __name__ == "__main__":
    main()
