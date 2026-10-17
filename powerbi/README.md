# Power BI Reconstruction Guide

> **Scope notice:** This project contains tested Python/SQLite assets and unexecuted Power BI DAX/Power Query reference code. **No `.pbix` file has been created or validated.** Power BI Desktop is required to create and visually validate the actual Power BI report; it does not run on an iPhone.

## Import the five dimension/fact tables

Use **Get Data → Text/CSV** to import from `data/synthetic/` and rename queries:

| File | Power BI table | Important column type |
|---|---|---|
| `departments.csv` | `DimDepartment` | IDs text |
| `gl_accounts.csv` | `DimGL` | IDs text |
| `fiscal_calendar.csv` | `DimDate` | `date`, `month_start` date; fiscal fields whole number |
| `budgets.csv` | `FactBudget` | `month_start` date; `budget_cents` whole number |
| `actuals.csv` | `FactActual` | `transaction_date` date; `actual_cents` whole number |

For illustrative ETL examples, see `power_query/budget_transform.m` and `power_query/actual_transform.m`. Each is a **separate** Power Query M query; create the `pCsvRoot` text parameter first and point it to the absolute path of the synthetic-data folder. Do not import the summary exports into the same semantic model as facts; doing so can create ambiguous totals.

## Create relationships (Model view)

Use **one-to-many** and **single-direction (dimension → fact)** relationships:

1. `DimDate[date]` → `FactBudget[month_start]` (active).
2. `DimDate[date]` → `FactActual[transaction_date]` (active).
3. `DimDepartment[department_id]` → `FactBudget[department_id]` (active).
4. `DimDepartment[department_id]` → `FactActual[department_id]` (active).
5. `DimGL[gl_account_id]` → `FactBudget[gl_account_id]` (active).
6. `DimGL[gl_account_id]` → `FactActual[gl_account_id]` (active).

Mark `DimDate` as the date table using `DimDate[date]` (unique continuous dates), and sort fiscal month labels or month names by `fiscal_month_index`.

## Create measures

In Desktop, create each expression from `dax/finance_measures.dax` as an individual **New measure**. Format USD measures as currency and percentage measures as %. DAX `DATESYTD(..., "9/30")` sets the fiscal year end to September 30.

## Suggested report pages

- **Executive Overview:** cards for FYTD budget, actual, variance, variance %, and labor share; monthly paired bar chart; dept variance matrix.
- **Department Deep Dive:** slicers for FY and department; labor/non-labor stacked bar; GL account matrix with conditional formatting.
- **GL Exception Review:** sorted unfavorable dollar drivers with thresholded exceptions; explain budget/actual reconciliation.

### Reconciliation before publishing a PBIX

Filter to FY2026 (Oct 2025–Sep 2026). Confirm sums match `data/processed/executive_kpis.json` and that rows from each department, GL and expense class reconcile. Verify October maps to fiscal month 1, September to fiscal month 12. Test full FY and partial FYTD with a month selection. Only then describe a working PBIX as verified.

## Phone-only limitation

You can inspect DAX, M code, datasets, SQL, SVG and the generated HTML report through GitHub/Codespaces using an iPhone. Creating a `.pbix` or independently validating DAX in Power BI Desktop requires a supported desktop environment. The reproducible HTML executive dashboard is this version's functional visualization deliverable.
