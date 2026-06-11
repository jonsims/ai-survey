"""Export enriched portfolio data for the v2 dashboard.

Adds: AMI ceiling rent per property, expense line items,
FMR market comp, LIHTC compliance fields.
"""

import json
import random
from pathlib import Path
import pandas as pd
import numpy as np

import dashboard_data as dd

random.seed(42)
np.random.seed(42)
OUTPUT = Path(__file__).resolve().parent / "output" / "v2_data.json"


def main():
    port = dd.load_portfolio().head(50)
    units = dd.load_unit_mix()
    units = units[units["property_id"].isin(port["property_id"])]
    data = {"properties": [], "summary": {}, "fmr_trajectory": [], "preservation": {}}

    for _, p in port.iterrows():
        opex = p["monthly_opex_per_unit"]
        insurance = round(opex * random.uniform(0.20, 0.30), 2)
        taxes = round(opex * random.uniform(0.25, 0.35), 2)
        maintenance = round(opex * random.uniform(0.20, 0.28), 2)
        management = round(opex - insurance - taxes - maintenance, 2)
        if management < 0:
            management = round(opex * 0.12, 2)

        ami_ceiling_rent = None
        headroom_pct = None
        if p["rent_restricted"] and pd.notna(p["ami_ceiling_pct"]) and p["ami_ceiling_pct"] > 0:
            vli = p["local_vli_4person"]
            ami_ceiling_rent = round((vli * (p["ami_ceiling_pct"] / 50)) / 12 * 0.30, 2)
            if p["avg_monthly_rent"] > 0:
                headroom_pct = round((ami_ceiling_rent - p["avg_monthly_rent"]) / p["avg_monthly_rent"] * 100, 1)

        annual_revenue = p["avg_monthly_rent"] * p["occupied_units"] * 12
        annual_opex = opex * p["total_units"] * 12
        noi = annual_revenue - annual_opex
        ds = p["annual_debt_service"]
        cash_flow = noi - ds if ds else noi
        dscr = round(noi / ds, 2) if ds and ds > 0 else None
        coc = round(cash_flow / p["acquisition_price"] * 100, 2) if p["acquisition_price"] > 0 else None

        prop = {
            "id": p["property_id"],
            "name": p["name"],
            "state": p["state"],
            "county": p["county_name"],
            "county_fips": p["county_fips"],
            "type": p["property_type"],
            "type_label": {"mhp_lot": "MHP", "lihtc_apartment": "LIHTC", "market_apartment": "Market"}[p["property_type"]],
            "units": int(p["total_units"]),
            "occupied": int(p["occupied_units"]),
            "occupancy_pct": round(p["occupied_units"] / p["total_units"] * 100, 1) if p["total_units"] > 0 else 0,
            "current_rent": round(p["avg_monthly_rent"], 0),
            "rent_restricted": bool(p["rent_restricted"]),
            "ami_ceiling_pct": int(p["ami_ceiling_pct"]) if pd.notna(p["ami_ceiling_pct"]) else None,
            "ami_ceiling_rent": ami_ceiling_rent,
            "headroom_pct": headroom_pct,
            "fmr_2br": round(p["local_fmr_2br"], 0),
            "expenses": {
                "insurance": insurance,
                "taxes": taxes,
                "maintenance": maintenance,
                "management": management,
                "total": round(opex, 2),
            },
            "annual_revenue": round(annual_revenue, 0),
            "annual_opex": round(annual_opex, 0),
            "noi": round(noi, 0),
            "debt_service": round(ds, 0) if ds else 0,
            "cash_flow": round(cash_flow, 0),
            "dscr": dscr,
            "cash_on_cash": coc,
            "acquisition_price": round(p["acquisition_price"], 0),
            "year_acquired": int(p["year_acquired"]),
        }
        data["properties"].append(prop)

    props = data["properties"]
    data["summary"] = {
        "total_properties": len(props),
        "total_units": sum(p["units"] for p in props),
        "avg_rent": round(np.mean([p["current_rent"] for p in props]), 0),
        "total_noi": round(sum(p["noi"] for p in props), 0),
        "total_value": round(sum(p["acquisition_price"] for p in props) / 1e6, 1),
        "states": sorted(set(p["state"] for p in props)),
        "by_type": {},
        "restricted_count": sum(1 for p in props if p["rent_restricted"]),
    }
    for t in ["mhp_lot", "lihtc_apartment", "market_apartment"]:
        subset = [p for p in props if p["type"] == t]
        data["summary"]["by_type"][t] = {
            "count": len(subset),
            "units": sum(p["units"] for p in subset),
            "avg_rent": round(np.mean([p["current_rent"] for p in subset]), 0) if subset else 0,
        }

    traj = dd.prepare_trajectory_data(top_n=8)
    data["fmr_trajectory"] = traj.to_dict("records")
    for r in data["fmr_trajectory"]:
        for k in r:
            if isinstance(r[k], float) and (pd.isna(r[k]) or np.isnan(r[k])):
                r[k] = None

    pres = dd.prepare_preservation_data()
    bucket_order = [f"{dd.CURRENT_YEAR}–{dd.CURRENT_YEAR+3}",
                    f"{dd.CURRENT_YEAR+4}–{dd.CURRENT_YEAR+5}",
                    f"{dd.CURRENT_YEAR+6}–{dd.CURRENT_YEAR+10}",
                    f"After {dd.CURRENT_YEAR+10}"]
    data["preservation"] = pres.groupby("bucket")["n_units"].sum().reindex(
        ["Already expired"] + bucket_order).fillna(0).astype(int).to_dict()

    OUTPUT.write_text(json.dumps(data, indent=2))
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size / 1024:.0f} KB)")
    print(f"Properties: {len(props)}, Restricted: {data['summary']['restricted_count']}")


if __name__ == "__main__":
    main()
