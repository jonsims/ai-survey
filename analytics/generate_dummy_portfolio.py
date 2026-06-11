"""Generate a realistic dummy portfolio for the rent-simulation demo.

Creates ~250 properties across 6 states, placed in counties where we have
FMR/AMI data. Mix of MHP lot-rent, LIHTC apartment, and market-rate apartment.
Outputs two CSVs: portfolio.csv and unit_mix.csv.
"""

import random
from pathlib import Path

import numpy as np
import pandas as pd

from lib import fmr_2br_county, income_limits_county, net_migration_by_county

OUTPUT = Path(__file__).resolve().parent.parent / "datasets" / "dummy"
random.seed(42)
np.random.seed(42)

STATES = {
    "48": ("TX", "Texas"),
    "12": ("FL", "Florida"),
    "04": ("AZ", "Arizona"),
    "37": ("NC", "North Carolina"),
    "45": ("SC", "South Carolina"),
    "32": ("NV", "Nevada"),
}

PROPERTY_TYPES = [
    ("mhp_lot", 0.45),
    ("lihtc_apartment", 0.35),
    ("market_apartment", 0.20),
]

MHP_NAMES = [
    "Sunridge", "Lakeview", "Pinewood", "Oakdale", "Cedar Creek",
    "Riverside", "Valley View", "Meadowbrook", "Hillcrest", "Shady Oaks",
    "Country Club", "Palm Harbor", "Eagle Landing", "Whispering Pines",
    "Rolling Hills", "Pecan Grove", "Silver Lake", "Bluebonnet",
    "Heritage Park", "Magnolia Place", "Willow Bend", "Cypress Point",
    "Green Acres", "Sunset Ridge", "Fox Run", "Quail Creek",
    "Sandy Creek", "Twin Oaks", "Stonegate", "Wildflower",
]

APT_NAMES = [
    "The Commons", "Arbor Walk", "Vista Pointe", "Parkside",
    "The Residences", "Harbor View", "Brookstone", "Creekside",
    "The Enclave", "Ridgeline", "Clearwater", "Stonewood",
    "The Preserve", "Highland Terrace", "Bayshore", "Aspen Grove",
    "The Landings", "Maple Court", "Westgate", "Southwind",
]


def pick_counties(n_per_state: int = 3) -> pd.DataFrame:
    """Pick real counties with FMR/AMI data, weighted by migration."""
    fmr = fmr_2br_county()
    il = income_limits_county()
    mig = net_migration_by_county()
    base = fmr.merge(il, on="fips_county").merge(mig, on="fips_county", how="left")
    base["net_migration_returns"] = base["net_migration_returns"].fillna(0)

    counties = []
    for state_fips, (postal, name) in STATES.items():
        state_df = base[base["fips_county"].str.startswith(state_fips)].copy()
        state_df = state_df.sort_values("net_migration_returns", ascending=False)
        picked = state_df.head(n_per_state)
        counties.append(picked)

    return pd.concat(counties, ignore_index=True)


def generate_portfolio(counties: pd.DataFrame, target_n: int = 250) -> pd.DataFrame:
    per_county = max(1, target_n // len(counties))
    rows = []
    pid = 1

    for _, county in counties.iterrows():
        n_props = random.randint(max(1, per_county - 2), per_county + 3)
        fmr_2br = county.get("fmr26_2", 1000)
        if pd.isna(fmr_2br):
            fmr_2br = 1000
        vli = county.get("vli_4person", 40000)
        if pd.isna(vli):
            vli = 40000

        for _ in range(n_props):
            ptype = random.choices(
                [t for t, _ in PROPERTY_TYPES],
                weights=[w for _, w in PROPERTY_TYPES],
            )[0]

            if ptype == "mhp_lot":
                name = random.choice(MHP_NAMES) + " " + random.choice(["MHP", "Estates", "Park", "Community"])
                total = random.randint(40, 220)
                occ_rate = random.uniform(0.82, 0.98)
                base_rent = fmr_2br * random.uniform(0.30, 0.55)
                restricted = random.random() < 0.15
                ami_ceil = random.choice([50, 60, 80]) if restricted else None
                opex = random.uniform(150, 350)
            elif ptype == "lihtc_apartment":
                name = random.choice(APT_NAMES) + " " + random.choice(["Apartments", "Place", "Village"])
                total = random.randint(48, 300)
                occ_rate = random.uniform(0.90, 0.99)
                base_rent = fmr_2br * random.uniform(0.55, 0.90)
                restricted = True
                ami_ceil = random.choice([50, 60, 60, 60, 80])
                opex = random.uniform(300, 550)
            else:
                name = random.choice(APT_NAMES) + " " + random.choice(["Lofts", "Crossing", "Heights"])
                total = random.randint(60, 250)
                occ_rate = random.uniform(0.88, 0.97)
                base_rent = fmr_2br * random.uniform(0.85, 1.30)
                restricted = False
                ami_ceil = None
                opex = random.uniform(350, 600)

            occupied = int(total * occ_rate)
            avg_rent = round(base_rent, 0)
            acq_year = random.randint(2010, 2024)
            cap_rate = random.uniform(0.045, 0.085)
            annual_noi = (avg_rent - opex) * total * 12 * occ_rate
            acq_price = annual_noi / cap_rate if cap_rate > 0 else 0
            annual_ds = acq_price * random.uniform(0.04, 0.065)

            rows.append({
                "property_id": f"P-{pid:04d}",
                "name": name,
                "state": county.get("state_postal", "TX"),
                "county_fips": county["fips_county"],
                "county_name": county.get("county_name", ""),
                "property_type": ptype,
                "total_units": total,
                "occupied_units": occupied,
                "avg_monthly_rent": round(avg_rent, 2),
                "rent_restricted": restricted,
                "ami_ceiling_pct": ami_ceil,
                "monthly_opex_per_unit": round(opex, 2),
                "annual_debt_service": round(annual_ds, 0),
                "year_acquired": acq_year,
                "acquisition_price": round(acq_price, 0),
                "local_fmr_2br": round(fmr_2br, 0),
                "local_vli_4person": round(vli, 0),
            })
            pid += 1

    return pd.DataFrame(rows)


def generate_unit_mix(portfolio: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, prop in portfolio.iterrows():
        total = prop["total_units"]
        avg_rent = prop["avg_monthly_rent"]
        ptype = prop["property_type"]
        fmr = prop["local_fmr_2br"]
        vli = prop["local_vli_4person"]
        ami_ceil = prop["ami_ceiling_pct"]

        if ptype == "mhp_lot":
            types = [("lot_standard", 0.7), ("lot_premium", 0.3)]
        else:
            types = [("1br", 0.25), ("2br", 0.45), ("3br", 0.30)]

        for utype, share in types:
            count = max(1, int(total * share))
            if utype == "lot_standard":
                rent = avg_rent * random.uniform(0.85, 1.0)
            elif utype == "lot_premium":
                rent = avg_rent * random.uniform(1.05, 1.25)
            elif utype == "1br":
                rent = avg_rent * random.uniform(0.75, 0.90)
            elif utype == "2br":
                rent = avg_rent * random.uniform(0.95, 1.05)
            else:
                rent = avg_rent * random.uniform(1.10, 1.30)

            if ami_ceil and ami_ceil > 0:
                ceiling = (vli * (ami_ceil / 50)) / 12 * 0.30
                if utype in ("1br", "lot_standard"):
                    ceiling *= 0.85
                elif utype in ("3br", "lot_premium"):
                    ceiling *= 1.10
            else:
                ceiling = None

            headroom = ((ceiling - rent) / rent * 100) if ceiling and rent > 0 else None

            rows.append({
                "property_id": prop["property_id"],
                "unit_type": utype,
                "count": count,
                "current_rent": round(rent, 2),
                "rent_ceiling": round(ceiling, 2) if ceiling else None,
                "headroom_pct": round(headroom, 1) if headroom is not None else None,
            })

    return pd.DataFrame(rows)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    print("Picking counties...")
    counties = pick_counties(n_per_state=8)
    print(f"  {len(counties)} counties across {len(STATES)} states")

    print("Generating portfolio...")
    portfolio = generate_portfolio(counties, target_n=50)
    portfolio.to_csv(OUTPUT / "portfolio.csv", index=False)
    print(f"  {len(portfolio)} properties → portfolio.csv")

    print("Generating unit mix...")
    units = generate_unit_mix(portfolio)
    units.to_csv(OUTPUT / "unit_mix.csv", index=False)
    print(f"  {len(units)} unit-type rows → unit_mix.csv")

    print(f"\nPortfolio breakdown:")
    print(portfolio["property_type"].value_counts().to_string())
    print(f"\nState breakdown:")
    print(portfolio["state"].value_counts().to_string())
    print(f"\nTotal units: {portfolio['total_units'].sum():,}")
    print(f"Average rent: ${portfolio['avg_monthly_rent'].mean():,.0f}")


if __name__ == "__main__":
    main()
