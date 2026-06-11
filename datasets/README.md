# Demo Dataset Cart — Mobile Home Park & Affordable Housing Analytics

A curated set of publicly-available datasets for prototyping AI-based data analytics on mobile-home-park and affordable-housing markets. Every file in this folder was downloaded from an official federal source on **2026-05-22** with no authentication required. Total footprint ~130 MB on disk (~50 MB excluding the optional Microsoft Access copy of LIHTC).

The seven datasets join on FIPS geography codes:
- **State FIPS (2 digits)** — e.g. `48` = Texas
- **County FIPS (3 digits)** — e.g. `201` = Harris County, TX
- **State + County FIPS (5 digits)** — e.g. `48201`
- **Census Tract FIPS (11 digits)** — e.g. `48201450500`

All seven are joinable in pandas/DuckDB without GIS dependencies. The LIHTC table is property-level with lat/lon; FMR, Income Limits, and QCT are tract or county-level; IRS Migration is county-pair-level.

---

## Files in this folder

```
datasets/
├── README.md                       ← this file
├── hud_lihtc/
│   ├── LIHTCPUB.csv                ← 54,102 LIHTC properties (1987–2023)
│   ├── LIHTCPUB_BIN.csv            ← same data at the Building Identification Number level
│   ├── LIHTCPUB.accdb              ← Microsoft Access copy (optional, 79 MB)
│   ├── LIHTC 2023 Data Dictionary.pdf
│   └── lihtcpub.zip                ← original archive
├── hud_fmr/
│   ├── FY26_FMRs_revised.xlsx      ← FY2026 county/CBSA-level Fair Market Rents
│   ├── fy2026_safmrs_revised.xlsx  ← FY2026 ZIP-level Small Area FMRs (metros only)
│   └── FMR_All_1983_2026.csv       ← 43-year rent history, all bedroom sizes
├── hud_income_limits/
│   └── Section8-FY26.xlsx          ← FY2026 AMI / 30% / 50% / 80% income limits
├── hud_qct/
│   ├── QCT2026.csv                 ← 14,496 Qualified Census Tracts (LIHTC basis boost)
│   ├── qct_data_2026.xlsx          ← Full underlying tract-level data (poverty %, income ratio)
│   ├── 2026-DDAs-Data-Used-to-Designate.xlsx ← Difficult Development Areas
│   └── QCT2026CSV.zip              ← original archive
└── irs_migration/
    ├── countyinflow2223.csv        ← 90,048 county-pair inflows (Filing Years 2022→2023)
    ├── countyoutflow2223.csv       ← matching outflows
    └── 2223migrationdata.zip       ← state-level Excel detail + documentation
```

---

## 1. HUD LIHTC Database

**File:** [hud_lihtc/LIHTCPUB.csv](hud_lihtc/LIHTCPUB.csv) (15 MB, 54,102 rows)
**Source:** [https://www.huduser.gov/portal/datasets/lihtc/property.html](https://www.huduser.gov/portal/datasets/lihtc/property.html)
**Coverage:** Every Low-Income Housing Tax Credit project placed in service 1987–2023.
**Updated:** April 2025 release (next release Spring 2026 for 2024 placements).
**License:** Public domain.

This is the spine of any affordable-housing analysis. Each row is one LIHTC project — typically a single property, occasionally a scattered-site deal. Has full property address + geocoded lat/lon, unit counts, credit type, year placed in service, and a long list of "is there other subsidy stacked on this deal?" flags (HOME, CDBG, HOPE VI, RAD, USDA 514/515/538, OZ funds, etc.).

### Most relevant columns

| Column | Meaning | Notes for analysis |
|---|---|---|
| `hud_id` | HUD's unique project identifier | Primary key. Format: `<state_id><sequence>`. |
| `project` | Project name | Often the trade name on the building. |
| `proj_add`, `proj_cty`, `proj_st`, `proj_zip` | Street address + city + state + ZIP | Geocoded; not always perfectly clean. |
| `latitude`, `longitude` | Project centroid | Use for spatial joins / mapping. |
| `fips2020`, `st2020`, `cnty2020` | 2020-vintage Census FIPS codes | Join key to ACS, QCT, FMR by county/tract. |
| `n_units` | Total project units | Headline size metric. |
| `li_units` | Low-income (income-restricted) units | Subset of `n_units`. The actual affordable count. |
| `n_0br`, `n_1br`, `n_2br`, `n_3br`, `n_4br` | Unit count by bedroom size | Joins to FMR by bedroom column (`fmr26_0`..`fmr26_4`). |
| `yr_pis` | Year placed in service | The clock starts here for the 15-year compliance period and 30-year extended-use period. |
| `yr_alloc` | Year credit was allocated | Usually 1–2 years before `yr_pis`. |
| `aff_period`, `aff_yrs` | Affordability commitment | How long the project must remain rent-restricted. |
| `inc_ceil`, `low_ceil` | Income ceilings (% AMI) for qualifying tenants | Typically 60% AMI for most projects, 80% for the income-averaging election. |
| `basis` | LIHTC type (9% or 4%) | 9% = competitive credits, more equity. 4% = bond-financed, lower equity. |
| `bond` | Tax-exempt bond flag | Indicates 4% deal. |
| `non_prof` | Non-profit ownership flag | Common in preservation deals. |
| `home`, `home_amt` | HOME funds flag + amount | Layered subsidy. |
| `cdbg`, `cdbg_amt` | Community Development Block Grant funds + amount | Layered subsidy. |
| `htf`, `htf_amt` | Housing Trust Fund flag + amount | Layered subsidy. |
| `fmha_514`, `fmha_515`, `fmha_538` | USDA Rural Housing program flags | Important for rural deals; often near MHP markets. |
| `qozf`, `qozf_amt` | Opportunity Zone Fund participation + amount | OZ structure flag. |
| `rentassist` | Whether project has rental assistance contract | Section 8 PBRA, RAD, etc. layered on. |
| `mff_ra` | Multifamily Mortgage Risk-share / Rental Assistance | Type of project-based rental assistance. |
| `rad` | RAD conversion flag | Public housing converted to PBRA / PBV under RAD. |
| `tcap`, `tcep` | Tax Credit Assistance / Exchange Program (2009 ARRA) | Recovery-era subsidy. |
| `scattered_site_cd` | Scattered-site project flag | Project covers multiple addresses. |
| `resyndication_cd` | Whether the project was re-syndicated | Important for preservation analysis (re-syndication = a second LIHTC allocation, typically with rehab). |

`LIHTCPUB_BIN.csv` is the same data exploded to the **Building Identification Number (BIN)** level — useful when a project contains multiple buildings with different placed-in-service dates.

---

## 2. HUD Fair Market Rents (FMR)

**Files:**
- [hud_fmr/FY26_FMRs_revised.xlsx](hud_fmr/FY26_FMRs_revised.xlsx) (360 KB) — FY2026 county/CBSA-level
- [hud_fmr/fy2026_safmrs_revised.xlsx](hud_fmr/fy2026_safmrs_revised.xlsx) (5.1 MB) — FY2026 ZIP-level Small Area FMRs (metros only)
- [hud_fmr/FMR_All_1983_2026.csv](hud_fmr/FMR_All_1983_2026.csv) (8.2 MB, 4,765 rows, 310 columns) — wide-format rent history 1983–2026 for every county

**Source:** [https://www.huduser.gov/portal/datasets/fmr.html](https://www.huduser.gov/portal/datasets/fmr.html)
**Updated:** Annually each October; revisions issued mid-FY.

FMRs are the rent ceilings HUD uses to set Section 8 voucher payment standards — effectively the federal benchmark for what an affordable rent looks like in any given county. For underwriting MHP lot rents and conventional affordable rents, FMRs are the single best public proxy for "what does the market support at the lower end?"

### Most relevant columns (FY2026 county file)

| Column | Meaning |
|---|---|
| `fips2026` / `fips` | 10-digit state + county + (optional sub-area) FIPS — join to LIHTC `fips2020` and IRS migration by trimming to 5 digits. |
| `state`, `county` | State postal code + county name. |
| `areaname26` | FMR area name (often a metro / CBSA, not always a single county). |
| `fmr26_0` | FY2026 efficiency / studio FMR |
| `fmr26_1` | FY2026 1-bedroom FMR |
| `fmr26_2` | FY2026 2-bedroom FMR (the most-used reference rent) |
| `fmr26_3` | FY2026 3-bedroom FMR |
| `fmr26_4` | FY2026 4-bedroom FMR |
| `msa26` | Whether the area is metropolitan or non-metropolitan |

The history file follows the same pattern with `fmr<YY>_<bedroom>` columns for every year 1983 → 2026. With 310 columns it's the cleanest single-file rent time-series for any AI analytics demo.

### SAFMR notes

Small Area FMRs are calculated at the **ZIP code** level inside designated metropolitan areas. The file `fy2026_safmrs_revised.xlsx` has one row per ZIP × bedroom-size combination. Use this when the analysis cares about *intra-metro* rent variation (e.g., comparing affordable rent in two ZIP codes in the Dallas-Fort Worth metro).

---

## 3. HUD Income Limits (FY 2026)

**File:** [hud_income_limits/Section8-FY26.xlsx](hud_income_limits/Section8-FY26.xlsx) (756 KB)
**Source:** [https://www.huduser.gov/portal/datasets/il.html](https://www.huduser.gov/portal/datasets/il.html)
**Updated:** Annually (FY2026 limits effective April 1, 2026).

Income Limits are the AMI (Area Median Income) tables that qualify tenants for LIHTC, HOME, Section 8, and other affordable programs. Every LIHTC project has rent ceilings tied to these limits. If you're sizing demand for affordable rentals in a county, the AMI table tells you what "60% AMI" actually translates to in dollars.

### Most relevant columns

| Column | Meaning |
|---|---|
| `fips2020` | 10-digit FIPS — join to LIHTC and FMR. |
| `State`, `County_Name`, `State_Alpha` | Geography labels. |
| `Median1` ... `Median8` | Median family income for households of size 1–8. |
| `ELI_1` ... `ELI_8` | **Extremely Low Income** limits (~30% AMI, sometimes higher of poverty guideline) for HH size 1–8. The income ceiling for the most-restricted LIHTC units. |
| `VLIL_1` ... `VLIL_8` | **Very Low Income** limits (50% AMI) for HH size 1–8. |
| `LIL_1` ... `LIL_8` | **Low Income** limits (80% AMI) for HH size 1–8. |
| `L80_1` ... `L80_8` | Often a duplicate of LIL — 80% of AMI. |
| `il50_p30`, `il50_p40`, ..., `il50_p80` | Percentage breakdowns of the 50% (Very Low Income) limit at various tenant-share points. |
| `MFI` | Area Median Family Income (the headline AMI number). |
| `MFI_FY26` | The FY2026 final MFI used to derive everything else. |

In an MHP affordability analysis, the most-used numbers are usually **`MFI`** (the AMI headline), **`ELI_4`** (30% AMI for a 4-person household), and **`VLIL_4`** (50% AMI for a 4-person household) — these set the underwriting demand brackets.

---

## 4. HUD Qualified Census Tracts (QCTs) and DDAs

**Files:**
- [hud_qct/QCT2026.csv](hud_qct/QCT2026.csv) (784 KB, 14,496 rows) — the list of qualifying tracts
- [hud_qct/qct_data_2026.xlsx](hud_qct/qct_data_2026.xlsx) (27 MB) — full tract-level data for every tract in the US (the underlying source data)
- [hud_qct/2026-DDAs-Data-Used-to-Designate.xlsx](hud_qct/2026-DDAs-Data-Used-to-Designate.xlsx) (3 MB) — Difficult Development Areas (county/ZIP-level cost-burden flags)

**Source:** [https://www.huduser.gov/portal/datasets/qct.html](https://www.huduser.gov/portal/datasets/qct.html)
**Updated:** Annually each September for the following calendar year.

QCT = tracts where ≥50% of households earn under 60% AMI, **or** poverty rate ≥25%. DDA = areas where rents/construction costs are high relative to AMI. Either designation gives a LIHTC deal a **30% basis boost** — i.e., the developer can claim credits on 130% of qualified basis instead of 100%. This is material to deal economics; one of the first filters you apply when screening LIHTC opportunities.

### Most relevant columns (QCT2026.csv)

| Column | Meaning |
|---|---|
| `cbsa` | Metropolitan/micropolitan area code |
| `statefp` | State FIPS (2 digits) |
| `cnty` | County FIPS (3 digits) |
| `stcnty` | State + county FIPS (5 digits) |
| `tract` | Census tract number |
| `qct_id` | Unique QCT identifier |
| `fips` | 11-digit state+county+tract FIPS — join to ACS tract data |

The presence of a row indicates QCT status; absence means the tract is not designated. For the richer detail (the *why* a tract is or isn't a QCT — poverty rate, AMI ratio, etc.), use `qct_data_2026.xlsx`.

### Most relevant columns (qct_data_2026.xlsx)

| Column | Meaning |
|---|---|
| `state`, `county`, `tract` | Geography labels and codes |
| `poverty_rate` | % of tract population below the poverty line |
| `income_factor` | Ratio of tract income to MFI of larger area |
| `pop` | Tract population |
| `qct_designated` | Boolean flag |

---

## 5. IRS County-to-County Migration (Filing Years 2022–2023)

**Files:**
- [irs_migration/countyinflow2223.csv](irs_migration/countyinflow2223.csv) (4.4 MB, 90,048 rows) — county pairs, inflow direction
- [irs_migration/countyoutflow2223.csv](irs_migration/countyoutflow2223.csv) (4.4 MB) — same pairs, outflow direction
- [irs_migration/2223migrationdata.zip](irs_migration/2223migrationdata.zip) (84 KB) — state-level Excel files + documentation

**Source:** [https://www.irs.gov/statistics/soi-tax-stats-migration-data-2022-2023](https://www.irs.gov/statistics/soi-tax-stats-migration-data-2022-2023)
**Updated:** Annually each summer for the prior two-year filing pair.

The single best public source for "where are people actually moving?" Built from year-over-year address changes on filed individual tax returns. Each row is a (destination, origin) county pair with the number of returns (≈ households), exemptions (≈ individuals), and aggregate AGI that migrated between them. Filed in the **2023 filing year** = generally calendar-year 2022 income, with the address change captured from comparing 2022→2023 filings.

### Most relevant columns

| Column | Meaning |
|---|---|
| `y2_statefips` | Destination state FIPS (where movers ended up) |
| `y2_countyfips` | Destination county FIPS |
| `y1_statefips` | Origin state FIPS (where movers came from) |
| `y1_countyfips` | Origin county FIPS |
| `y1_state` | Origin state postal code |
| `y1_countyname` | Origin county name (or summary row label) |
| `n1` | Number of returns (≈ households) that migrated |
| `n2` | Number of personal exemptions claimed (≈ individuals) |
| `agi` | Aggregate adjusted gross income, in thousands of dollars |

### Special summary rows to watch for

The dataset embeds summary rows where `y1_countyfips = '000'` or other sentinel codes:

- `96` / `000`: **Total Migration — US and Foreign** (everyone who moved into the destination county from anywhere, including abroad)
- `97` / `000`: **Total Migration — US** (excluding foreign)
- `98` / `000`: **Total Migration — Same State**
- `57` / `009`: **Foreign migration** rolled up
- A `96` / `036` style code with a state alias: **All movers from that state**

For deal-level analysis you want the actual county-pair rows, not the summary rows. Filter to `y1_countyfips != '000'`.

`countyinflow` and `countyoutflow` are mirror datasets — every row in one has a complementary row in the other. Use whichever direction your question favors.

---

## What's NOT in this folder (but easy to add)

A few sources from the underlying research doc that I deliberately skipped for this demo cart, with the reason:

| Dataset | Why skipped | How to add later |
|---|---|---|
| **ACS 5-year housing tables** (mobile home counts, tenure, median income) | Census API now requires a free API key | Register at [api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html), then use `tidycensus` (R) or `pygris` (Python) to pull tables B25024, B25032, B19013, B25064, B25077. Five minutes including verification email. |
| **EPA EJScreen** | The full 2024 file is 5.2 GB | For a state-filtered demo, download from Zenodo mirror at [zenodo.org/records/14767363](https://zenodo.org/records/14767363) and filter to the target state's FIPS. |
| **NHPD** (preservation database) | Requires registration | Register at [preservationdatabase.org](https://preservationdatabase.org/accessing-the-database/), then download quarterly Excel at country/state/county level. |
| **HUD CHAS (Comprehensive Housing Affordability Strategy)** | Direct file URLs are JavaScript-rendered | Use the [CHAS data download tool](https://www.huduser.gov/portal/datasets/cp.html) UI to get the 2018–2022 county-level zip. CHAS is the HUD-curated ACS housing data with cost-burden breakdowns — a good substitute for raw ACS if you want to skip the API key. |
| **TDHCA Texas MH ownership records** | Portal requires interactive form submission with criteria selection | Visit [mhweb.tdhca.state.tx.us/mhweb/download_title_info.jsp](https://mhweb.tdhca.state.tx.us/mhweb/download_title_info.jsp), fill the form (date range + county), and download. |
| **Fannie Mae Multifamily Loan Performance** | Requires free Data Dynamics registration | [Register here](https://capitalmarkets.fanniemae.com/credit-risk-transfer/multifamily-credit-risk-transfer/multifamily-loan-performance-data); main file is CSV with ~71K loans and an MHC flag. |
| **FEMA NFHL** | Shapefile only; requires GIS stack | Download per-county shapefile from [FEMA Map Service Center](https://msc.fema.gov/portal/advanceSearch). |

---

## Suggested demo joins

A few starter queries that will exercise the dataset cart:

1. **"What share of LIHTC units are in QCTs?"** — Inner join `LIHTCPUB.csv` to `QCT2026.csv` on the 11-digit tract FIPS (`LIHTCPUB.fips2020` matches `QCT2026.fips`). Compare unit counts in/out.

2. **"For counties seeing net in-migration in 2022–2023, what is their FMR vs. AMI ratio?"** — Aggregate IRS migration inflows minus outflows by destination county. Join to FMR (2BR) and Income Limits (`VLIL_4`). Compute `fmr26_2 / (VLIL_4 / 12)` as a rough rent burden index.

3. **"Where are LIHTC projects with rural USDA layered subsidies?"** — Filter `LIHTCPUB.csv` to `fmha_514 == 1 OR fmha_515 == 1 OR fmha_538 == 1`, map by lat/lon. Cross-reference with non-metropolitan FMR areas (`msa26 == 'N'`).

4. **"Which Texas counties are gaining the most households (by IRS migration) AND already have a constrained LIHTC supply (low LIHTC units per capita)?"** — Aggregate IRS inflows to Texas county level (`y2_statefips == '48'`), count LIHTC units by county from `LIHTCPUB.csv`, divide by ACS county population. Rank.

5. **"What's the longitudinal rent trajectory for counties in the demo focus region?"** — Use the FMR history CSV (`FMR_All_1983_2026.csv`) to chart 2BR rent growth from 1990 → 2026 for the target counties. Compare to AGI growth from the IRS data over the same window.

The 11-digit FIPS code (`state + county + tract`) is the universal joiner — every dataset in this folder either includes it or can be aggregated to a level that does.

---

## File integrity

| File | SHA notes |
|---|---|
| All HUD files | Served from huduser.gov over HTTPS; LIHTC file last-modified 2025-12-09. |
| IRS migration | Served from irs.gov over HTTPS. |
| Downloaded | 2026-05-22 ~12:55 ET. |

For reproducibility, the download commands are recorded in the project's session history; this directory can be rebuilt from scratch in under five minutes given an internet connection.
