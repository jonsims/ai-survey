"""Export all analytics data as JSON for the static HTML dashboard."""

import json
from pathlib import Path
import pandas as pd
import dashboard_data as dd

OUTPUT = Path(__file__).resolve().parent / "output" / "dashboard_data.json"


def main():
    data = {}

    # Portfolio summary
    port = dd.load_portfolio()
    data["portfolio"] = {
        "total_properties": len(port),
        "total_units": int(port["total_units"].sum()),
        "avg_rent": round(port["avg_monthly_rent"].mean(), 0),
        "states": sorted(port["state"].unique().tolist()),
        "by_type": port.groupby("property_type")["total_units"].sum().to_dict(),
        "total_value": round(port["acquisition_price"].sum() / 1e6, 1),
    }

    # Top properties for listings tab
    props = port.nlargest(12, "total_units").to_dict("records")
    for p in props:
        for k, v in p.items():
            if pd.isna(v):
                p[k] = None
    data["listings"] = props

    # Pipeline by type
    type_map = {"mhp_lot": "MHP Lot Rent", "lihtc_apartment": "LIHTC Apartment", "market_apartment": "Market Rate"}
    by_state_type = port.groupby(["state", "property_type"]).agg(
        count=("property_id", "count"),
        units=("total_units", "sum"),
        value=("acquisition_price", "sum"),
    ).reset_index()
    by_state_type["property_type"] = by_state_type["property_type"].map(type_map)
    by_state_type["value"] = (by_state_type["value"] / 1e6).round(1)
    data["pipeline"] = by_state_type.to_dict("records")

    # Migration top 20
    mig = dd.prepare_migration_data(top_n=20)
    data["migration"] = mig[["label", "net_migration_returns", "lihtc_total_units"]].to_dict("records")

    # Burden top 25
    burden = dd.prepare_burden_data().head(25)
    data["burden"] = burden[["label", "fmr26_2", "vli_4person", "burden_ratio"]].to_dict("records")
    for r in data["burden"]:
        for k in r:
            if pd.isna(r[k]):
                r[k] = None
            elif isinstance(r[k], float):
                r[k] = round(r[k], 2)

    # Preservation buckets
    pres = dd.prepare_preservation_data()
    bucket_order = ["Already expired", f"{dd.CURRENT_YEAR}–{dd.CURRENT_YEAR+3}",
                    f"{dd.CURRENT_YEAR+4}–{dd.CURRENT_YEAR+5}",
                    f"{dd.CURRENT_YEAR+6}–{dd.CURRENT_YEAR+10}",
                    f"After {dd.CURRENT_YEAR+10}"]
    by_bucket = pres.groupby("bucket")["n_units"].sum().reindex(bucket_order).fillna(0).astype(int).to_dict()
    data["preservation"] = by_bucket

    # FMR trajectory
    traj = dd.prepare_trajectory_data(top_n=8)
    data["trajectory"] = traj.to_dict("records")

    # Simulation base data
    sim_base = dd.simulate_rent_change(0, 0, 0, 1)
    data["sim_properties"] = sim_base[
        ["property_id", "name", "state", "county_name", "property_type",
         "total_units", "current_rent", "current_noi", "dscr"]
    ].head(50).to_dict("records")
    for r in data["sim_properties"]:
        for k in r:
            if isinstance(r[k], float) and pd.isna(r[k]):
                r[k] = None

    OUTPUT.write_text(json.dumps(data, indent=2))
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
