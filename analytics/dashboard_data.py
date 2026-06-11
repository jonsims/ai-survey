"""Data prep + projection math for the interactive dashboard.

Calls lib.py for raw data, then shapes it for Plotly/Folium rendering
and adds projection logic for the slider-driven scenarios.
"""

from pathlib import Path

import pandas as pd
import numpy as np

from lib import (
    TARGET_STATE_FIPS,
    TARGET_STATE_NAME,
    county_name_map,
    filter_to_state,
    fmr_2br_county,
    income_limits_county,
    lihtc_units_by_county,
    load_fmr_history,
    load_lihtc,
    net_migration_by_county,
)

CURRENT_YEAR = 2026
DUMMY_DIR = Path(__file__).resolve().parent.parent / "datasets" / "dummy"


def prepare_map_data() -> pd.DataFrame:
    df = load_lihtc()
    df = df[df["fips_county"].notna()]
    df = filter_to_state(df, "fips_county")

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df[df["latitude"].notna() & df["longitude"].notna()]

    df["yr_pis"] = pd.to_numeric(df["yr_pis"], errors="coerce")
    df["aff_yrs_used"] = pd.to_numeric(df["aff_yrs"], errors="coerce").fillna(30)
    df["expiration_year"] = df["yr_pis"] + df["aff_yrs_used"]

    def status(row):
        exp = row["expiration_year"]
        if pd.isna(exp):
            return "Unknown"
        if exp < CURRENT_YEAR:
            return "Expired"
        if exp <= CURRENT_YEAR + 5:
            return "Expiring ≤5yr"
        if exp <= CURRENT_YEAR + 10:
            return "Expiring 5–10yr"
        return "Active (10yr+)"

    df["status"] = df.apply(status, axis=1)
    return df[["project", "proj_add", "proj_cty", "latitude", "longitude",
               "n_units", "li_units", "yr_pis", "expiration_year", "status"]].copy()


def prepare_migration_data(top_n: int = 25) -> pd.DataFrame:
    lihtc = lihtc_units_by_county()
    migration = net_migration_by_county()
    names = county_name_map()

    df = migration.merge(lihtc, on="fips_county", how="left")
    df[["lihtc_total_units"]] = df[["lihtc_total_units"]].fillna(0)
    df = df.merge(names, on="fips_county", how="left")
    df["label"] = df["county_name"].fillna("") + ", " + df["state"].fillna("")
    return df.nlargest(top_n, "net_migration_returns")


def prepare_burden_data() -> pd.DataFrame:
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


def project_burden(burden_df: pd.DataFrame, fmr_growth_pct: float, years: int = 5) -> pd.DataFrame:
    rows = []
    for _, r in burden_df.iterrows():
        for y in range(1, years + 1):
            projected_fmr = r["fmr26_2"] * (1 + fmr_growth_pct / 100) ** y
            projected_ratio = projected_fmr / r["monthly_30pct_vli"]
            rows.append({"label": r["label"], "year": CURRENT_YEAR + y,
                         "projected_fmr": projected_fmr, "projected_ratio": projected_ratio})
    return pd.DataFrame(rows)


def prepare_preservation_data() -> pd.DataFrame:
    df = load_lihtc()
    df = df[df["fips_county"].notna()]
    df = filter_to_state(df, "fips_county")

    df["yr_pis"] = pd.to_numeric(df["yr_pis"], errors="coerce")
    df = df[df["yr_pis"].notna() & (df["yr_pis"] < 9000)]
    df["aff_yrs_used"] = pd.to_numeric(df["aff_yrs"], errors="coerce").fillna(30)
    df["expiration_year"] = df["yr_pis"] + df["aff_yrs_used"]

    def bucket(exp):
        if exp < CURRENT_YEAR:
            return "Already expired"
        elif exp <= CURRENT_YEAR + 3:
            return f"{CURRENT_YEAR}–{CURRENT_YEAR+3}"
        elif exp <= CURRENT_YEAR + 5:
            return f"{CURRENT_YEAR+4}–{CURRENT_YEAR+5}"
        elif exp <= CURRENT_YEAR + 10:
            return f"{CURRENT_YEAR+6}–{CURRENT_YEAR+10}"
        else:
            return f"After {CURRENT_YEAR+10}"

    df["bucket"] = df["expiration_year"].apply(bucket)
    names = county_name_map()
    df = df.merge(names, on="fips_county", how="left")
    df["label"] = df["county_name"].fillna(df["fips_county"]) + ", " + df["state"].fillna("")
    return df


def prepare_trajectory_data(top_n: int = 10):
    migration = net_migration_by_county()
    migration = filter_to_state(migration, "fips_county")
    top_fips = migration.nlargest(top_n, "net_migration_returns")["fips_county"].tolist()

    fmr = load_fmr_history()
    fmr["fips_county"] = fmr["fips"].str.zfill(10).str[:5]
    fmr = filter_to_state(fmr, "fips_county")
    fmr = fmr[fmr["cousub"].fillna("99999") == "99999"]
    fmr = fmr[fmr["fips_county"].isin(top_fips)]

    names = county_name_map()
    fmr = fmr.merge(names, on="fips_county", how="left")
    fmr["label"] = fmr["county_name"].fillna(fmr["fips_county"])

    year_cols = [("fmr90_2", 1990), ("fmr95_2", 1995), ("fmr00_2", 2000),
                 ("fmr05_2", 2005), ("fmr10_2", 2010), ("fmr15_2", 2015),
                 ("fmr20_2", 2020), ("fmr26_2", 2026)]
    available = [(c, y) for c, y in year_cols if c in fmr.columns]

    rows = []
    for _, r in fmr.iterrows():
        for col, yr in available:
            val = r.get(col)
            if isinstance(val, str):
                val = float(val.replace("$", "").replace(",", "")) if val.replace("$", "").replace(",", "").replace(".", "").isdigit() else np.nan
            else:
                val = float(val) if pd.notna(val) else np.nan
            if pd.notna(val):
                rows.append({"label": r["label"], "fips_county": r["fips_county"],
                             "year": yr, "fmr_2br": val, "projected": False})

    return pd.DataFrame(rows)


def project_trajectory(traj_df: pd.DataFrame, fmr_growth_pct: float, projection_years: int = 10):
    base = traj_df[traj_df["year"] == 2026].copy()
    proj_rows = []
    for _, r in base.iterrows():
        for y in range(1, projection_years + 1):
            proj_rows.append({
                "label": r["label"], "fips_county": r["fips_county"],
                "year": 2026 + y,
                "fmr_2br": r["fmr_2br"] * (1 + fmr_growth_pct / 100) ** y,
                "projected": True,
            })
    return pd.concat([traj_df, pd.DataFrame(proj_rows)], ignore_index=True)


# ── Rent Simulation (dummy portfolio) ──────────────────────────────────

def load_portfolio() -> pd.DataFrame:
    return pd.read_csv(DUMMY_DIR / "portfolio.csv")


def load_unit_mix() -> pd.DataFrame:
    return pd.read_csv(DUMMY_DIR / "unit_mix.csv")


def simulate_rent_change(
    rent_increase_pct: float,
    expense_growth_pct: float = 2.0,
    occupancy_delta_pct: float = 0.0,
    years: int = 5,
) -> pd.DataFrame:
    """Project NOI and ceiling impact for every property in the portfolio."""
    port = load_portfolio()
    units = load_unit_mix()

    rows = []
    for _, p in port.iterrows():
        prop_units = units[units["property_id"] == p["property_id"]]
        total_u = p["total_units"]
        occ_rate = p["occupied_units"] / total_u if total_u > 0 else 0

        current_revenue = p["avg_monthly_rent"] * p["occupied_units"] * 12
        current_opex = p["monthly_opex_per_unit"] * total_u * 12
        current_noi = current_revenue - current_opex

        proj_rent = p["avg_monthly_rent"] * (1 + rent_increase_pct / 100) ** years
        proj_opex = p["monthly_opex_per_unit"] * (1 + expense_growth_pct / 100) ** years
        proj_occ = min(1.0, max(0.5, occ_rate + occupancy_delta_pct / 100))
        proj_occupied = int(total_u * proj_occ)

        hit_ceiling = False
        effective_rent = proj_rent
        if p["rent_restricted"] and pd.notna(p["ami_ceiling_pct"]) and p["ami_ceiling_pct"] > 0:
            vli = p["local_vli_4person"]
            ceiling = (vli * (p["ami_ceiling_pct"] / 50)) / 12 * 0.30
            if proj_rent > ceiling:
                hit_ceiling = True
                effective_rent = ceiling

        proj_revenue = effective_rent * proj_occupied * 12
        proj_total_opex = proj_opex * total_u * 12
        proj_noi = proj_revenue - proj_total_opex
        noi_change = proj_noi - current_noi
        ds = p["annual_debt_service"]
        dscr = proj_noi / ds if ds and ds > 0 else None
        cash_yield = proj_noi / p["acquisition_price"] * 100 if p["acquisition_price"] > 0 else None

        rows.append({
            "property_id": p["property_id"],
            "name": p["name"],
            "state": p["state"],
            "county_name": p["county_name"],
            "property_type": p["property_type"],
            "total_units": total_u,
            "current_rent": round(p["avg_monthly_rent"], 0),
            "projected_rent": round(effective_rent, 0),
            "rent_capped": hit_ceiling,
            "current_noi": round(current_noi, 0),
            "projected_noi": round(proj_noi, 0),
            "noi_change": round(noi_change, 0),
            "noi_change_pct": round(noi_change / current_noi * 100, 1) if current_noi else 0,
            "dscr": round(dscr, 2) if dscr else None,
            "cash_yield_pct": round(cash_yield, 2) if cash_yield else None,
            "projected_occupancy": round(proj_occ * 100, 1),
        })

    return pd.DataFrame(rows)
