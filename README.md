# Carbon Footprint Lab — V7.3 (Complete English Edition)

An English-language personal carbon footprint learning application built with Python, Streamlit, Pandas, and SQLite. It includes all previous functionality from V1 through V7.2.

## Installation

Use Python 3.10+ and run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The dashboard normally opens at `http://localhost:8501`.

## Features

- Add dated personal activities and calculate emission estimates.
- Select electricity, regular gasoline, premium gasoline, diesel B, and illustrative travel categories.
- Record factors and source metadata in SQLite, including a snapshot of the factor used at registration.
- Apply documented Brazilian electricity factors for 2023–2025 with clearly stated verification limitations.
- Import verified 2026 MCTI monthly SIN electricity factors using a CSV and the original workbook SHA-256. **2026 values are not bundled.**
- Estimate combustion fossil CO₂ plus CH₄ and N₂O as CO₂e for Brazilian fuel blends. Report biogenic CO₂ separately.
- Filter, chart, inspect, delete, and export activities as CSV.
- Recognize Portuguese category names from existing databases created by earlier versions.

## Accounting limitations

This is an educational prototype, **not** a certified GHG inventory. Annual electricity factors and fuel combustion calculations have different accounting boundaries. The fuel model uses explicit net calorific value approximations, IPCC default factors, and AR5 GWP assumptions; results are derived estimates rather than official factors for every vehicle and blend. The biogenic CO₂ component is estimated and excluded from the combustion CO₂e total. Illustrative categories are never official emission estimates. A full personal footprint would also require food, goods, services, and additional indirect emissions.

The 2026 monthly factor importer accepts independently verified CSV rows with columns `year,month,factor_tco2_mwh`. Providing a SHA-256 hash does **not** automatically verify that the CSV values match the workbook; the user must check the values.

## Data compatibility

The database schema is preserved. If you already have `carbon_personal.sqlite3` from V7.2, **back it up first**, then copy it into this project's root directory. Historical Portuguese categories are translated when displayed. Existing numeric snapshots are not recalculated.

## Automated tests

```bash
python -m unittest discover -s tests -v
```

## Sources

- [MCTI/SIRENE emission factors](https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao)
- [ANP](https://www.gov.br/anp/pt-br)
- [IPCC 2006 Guidelines, Mobile Combustion](https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_3_Ch3_Mobile_Combustion.pdf)

## Release notes

**V7.3:** Standardized the dashboard, messages, category labels, code comments, documentation, and tests in English; retained the original formulas and historical-record compatibility.

## Version history

Historical source snapshots are in [`history/`](history/README.md). V1–V6 were available only as a combined V6 snapshot; no separate V1–V5 releases are claimed. The root contains V7.3 in English.
