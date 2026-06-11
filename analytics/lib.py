"""Shared data loaders for the analytics demo.

All datasets in ../datasets/ are joinable on FIPS codes. This module centralizes
loading + cleaning so each story script can focus on its analysis.
"""

from pathlib import Path
import pandas as pd

DATASETS = Path(__file__).resolve().parent.parent / "datasets"

IRS_SUMMARY_STATE_CODES = {"57", "96", "97", "98"}

# Target state for the demo. Two-digit state FIPS.
# 48 = Texas (used as the demo geography for this fictional company).
TARGET_STATE_FIPS = "48"
TARGET_STATE_NAME = "Texas"


def filter_to_state(df: pd.DataFrame, fips_col: str, state_fips: str = TARGET_STATE_FIPS) -> pd.DataFrame:
    """Return rows where the 5-digit county FIPS starts with the state code."""
    return df[df[fips_col].astype(str).str.startswith(state_fips)].copy()


def load_lihtc() -> pd.DataFrame:
    """Property-level LIHTC table with a clean 5-digit county FIPS.

    Note: HUD encodes missing FIPS values as literal "." in the CSV. About 21%
    of rows (~11,300) lack a usable county FIPS. They retain a state postal
    code in `proj_st` but no machine-readable county; for now we drop them
    from county-level aggregations and report the loss.
    """
    df = pd.read_csv(
        DATASETS / "hud_lihtc" / "LIHTCPUB.csv",
        low_memory=False,
        dtype=str,
    )
    df["st2020"] = df["st2020"].replace(".", pd.NA)
    df["cnty2020"] = df["cnty2020"].replace(".", pd.NA)
    df["n_units"] = pd.to_numeric(df["n_units"], errors="coerce").fillna(0).astype(int)
    df["li_units"] = pd.to_numeric(df["li_units"], errors="coerce").fillna(0).astype(int)

    has_geo = df["st2020"].notna() & df["cnty2020"].notna()
    df["fips_county"] = pd.NA
    df.loc[has_geo, "fips_county"] = (
        df.loc[has_geo, "st2020"].str.zfill(2)
        + df.loc[has_geo, "cnty2020"].str.zfill(3)
    )
    return df


def lihtc_units_by_county() -> pd.DataFrame:
    """LIHTC project + unit counts aggregated to the county level.

    Drops projects without a 5-digit county FIPS. See `load_lihtc` for context.
    """
    df = load_lihtc()
    df = df[df["fips_county"].notna()]
    agg = df.groupby("fips_county", dropna=True).agg(
        lihtc_projects=("hud_id", "count"),
        lihtc_total_units=("n_units", "sum"),
        lihtc_low_income_units=("li_units", "sum"),
    ).reset_index()
    return agg


def load_irs_migration(direction: str) -> pd.DataFrame:
    """IRS county-to-county migration data with summary rows removed.

    direction: 'inflow' (each row is who moved into a county) or 'outflow'.
    Returns columns: fips_y1, fips_y2, y1_countyname, n1, n2, agi.
    """
    fname = f"county{direction}2223.csv"
    df = pd.read_csv(
        DATASETS / "irs_migration" / fname,
        encoding="latin-1",  # IRS CSVs contain non-UTF8 county names (e.g. Doña Ana)
        dtype={
            "y2_statefips": str,
            "y2_countyfips": str,
            "y1_statefips": str,
            "y1_countyfips": str,
            "y1_state": str,
            "y1_countyname": str,
        },
    )
    df["fips_y2"] = df["y2_statefips"].str.zfill(2) + df["y2_countyfips"].str.zfill(3)
    df["fips_y1"] = df["y1_statefips"].str.zfill(2) + df["y1_countyfips"].str.zfill(3)

    is_summary = (
        df["y1_statefips"].isin(IRS_SUMMARY_STATE_CODES)
        | df["y2_statefips"].isin(IRS_SUMMARY_STATE_CODES)
        | (df["y1_countyfips"] == "000")
        | (df["y2_countyfips"] == "000")
    )
    return df.loc[~is_summary].copy()


def county_name_map() -> pd.DataFrame:
    """FIPS → county name + state, built from IRS migration partner rows.

    In the inflow file the partner is y1 (origin); in outflow it's y2
    (destination). The partner side is what carries the human-readable
    `*_countyname` and `*_state` columns. Combining both files gives a
    complete FIPS → name lookup.
    """
    inflow = load_irs_migration("inflow")
    outflow = load_irs_migration("outflow")
    a = inflow[["fips_y1", "y1_state", "y1_countyname"]].rename(
        columns={"fips_y1": "fips_county", "y1_state": "state", "y1_countyname": "county_name"}
    )
    b = outflow[["fips_y2", "y2_state", "y2_countyname"]].rename(
        columns={"fips_y2": "fips_county", "y2_state": "state", "y2_countyname": "county_name"}
    )
    return pd.concat([a, b], ignore_index=True).drop_duplicates("fips_county")


def net_migration_by_county() -> pd.DataFrame:
    """Per-county net IRS migration (inflow - outflow) for FY 2022–23.

    Returns: fips_county, inflow_returns, outflow_returns, net_migration_returns,
    inflow_individuals, outflow_individuals, net_migration_individuals.
    """
    inflow = load_irs_migration("inflow")
    outflow = load_irs_migration("outflow")

    in_sum = inflow.groupby("fips_y2").agg(
        inflow_returns=("n1", "sum"),
        inflow_individuals=("n2", "sum"),
        inflow_agi=("agi", "sum"),
    )
    out_sum = outflow.groupby("fips_y1").agg(
        outflow_returns=("n1", "sum"),
        outflow_individuals=("n2", "sum"),
        outflow_agi=("agi", "sum"),
    )
    df = pd.concat([in_sum, out_sum], axis=1).fillna(0).reset_index()
    df = df.rename(columns={"index": "fips_county"})
    df["net_migration_returns"] = df["inflow_returns"] - df["outflow_returns"]
    df["net_migration_individuals"] = df["inflow_individuals"] - df["outflow_individuals"]
    df["net_migration_agi"] = df["inflow_agi"] - df["outflow_agi"]
    return df


def load_fmr_history() -> pd.DataFrame:
    """Wide-format FMR history 1983-2026, all bedroom sizes, by county/sub-area.

    Returns 4,765 rows × 310 columns. Includes `fmr<YY>_<bed>` columns for
    every year from 1983 through 2026 and bedroom sizes 0-4. The `fips` column
    is a 10-digit state+county+sub-area code; first 5 digits are county FIPS.
    """
    df = pd.read_csv(
        DATASETS / "hud_fmr" / "FMR_All_1983_2026.csv",
        encoding="latin-1",
        dtype={"fips": str, "state": str, "county": str, "cousub": str},
        low_memory=False,
    )
    df["fips_county"] = df["fips"].str.zfill(10).str[:5]
    return df


def fmr_2br_county() -> pd.DataFrame:
    """Per-county FY26 2BR FMR plus a few historical reference years."""
    df = load_fmr_history()
    # Many counties have multiple sub-areas (cousub); collapse to county-level
    # by taking the area-name primary row (cousub == '99999' is the county-as-a-whole
    # convention in HUD's FMR file).
    primary = df[df["cousub"].fillna("99999") == "99999"].copy()
    if primary.empty:
        primary = df.drop_duplicates("fips_county")
    cols = ["fips_county", "state", "county", "areaname26",
            "fmr26_2", "fmr20_2", "fmr15_2", "fmr10_2", "fmr05_2",
            "fmr00_2", "fmr95_2", "fmr90_2"]
    cols = [c for c in cols if c in primary.columns]
    result = primary[cols].drop_duplicates("fips_county").copy()
    fmr_cols = [c for c in result.columns if c.startswith("fmr")]
    for c in fmr_cols:
        result[c] = result[c].astype(str).str.replace(r"[\$,]", "", regex=True)
        result[c] = pd.to_numeric(result[c], errors="coerce")
    return result


def load_income_limits() -> pd.DataFrame:
    """HUD FY2026 Income Limits with clean 5-digit county FIPS.

    The HUD `fips` column is a 9-digit area code; state+county is constructed
    from the `state` and `county` numeric columns instead.
    """
    df = pd.read_excel(
        DATASETS / "hud_income_limits" / "Section8-FY26.xlsx", sheet_name=0
    )
    df["fips_county"] = (
        df["state"].astype(int).astype(str).str.zfill(2)
        + df["county"].astype(int).astype(str).str.zfill(3)
    )
    return df


def income_limits_county() -> pd.DataFrame:
    """Per-county FY26 AMI + 50%/30%/80% income limits at 4-person HH size."""
    df = load_income_limits()
    df = df.drop_duplicates("fips_county", keep="first")
    cols = ["fips_county", "stusps", "County_Name", "median2026",
            "l50_4", "ELI_4", "l80_4"]
    return df[cols].rename(columns={
        "stusps": "state_postal",
        "County_Name": "county_name",
        "median2026": "ami_2026",
        "l50_4": "vli_4person",      # 50% AMI for a 4-person household
        "ELI_4": "eli_4person",      # 30% AMI for a 4-person household
        "l80_4": "li80_4person",     # 80% AMI for a 4-person household
    })
