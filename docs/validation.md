# Validation Report — v0.1

## Commands

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests -v
```

The first command generates and loads the seeded data, executes integrity checks and renders the report. The second command runs calendar boundary, grain, reconciliation, classification, YTD, foreign-key and determinism tests.

## Expected benchmark, synthetic FY2026

| Metric | Expected |
|---|---:|
| Synthetic transactions | 3,465 |
| Monthly department-GL budget rows (24 months) | 1,152 |
| Calendar days (24 months) | 730 |
| FY2026 Budget | $31,109,140.29 |
| FY2026 Actual | $31,352,851.47 |
| FY2026 Expense variance: Actual - Budget | +$243,711.18 |
| Expected tests | 11 passing |

If any value changes unexpectedly, inspect the generator, fiscal definitions and validations before changing the benchmark. Runtime SQLite DB files are **not** committed; recreate with `python3 scripts/build.py`.

## Explicit validation boundaries

- **Executed and tested:** Python 3 standard-library generator, SQLite DDL/view, SQLite loader and reporting, HTML and SVG generation.
- **Reviewed but not executed in corresponding product:** T-SQL examples, Power Query M examples, DAX measures and Power BI relationships.
- **Not included:** Power BI `.pbix`, production ETL scheduler, cloud SQL instance, user authentication, finance-system connectors.

No real company records, private identifiers, or employer-owned SQL appear in this repository.
