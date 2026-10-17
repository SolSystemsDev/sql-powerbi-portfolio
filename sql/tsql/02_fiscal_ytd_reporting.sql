/* SQL Server reporting queries, assuming 01_schema_and_views.sql and imported CSV rows.
   FY2026 starts 2025-10-01. Variance cents = actual cents - budget cents. */
DECLARE @FiscalYear INT = 2026;
DECLARE @FiscalMonthThrough INT = 12; -- use 1 through 12 for a mid-year FYTD snapshot

-- Department / class matrix at fiscal-YTD grain.
SELECT department_name, expense_class,
       CAST(SUM(budget_cents) / 100.0 AS DECIMAL(19,2)) AS budget_usd,
       CAST(SUM(actual_cents) / 100.0 AS DECIMAL(19,2)) AS actual_usd,
       CAST(SUM(variance_cents) / 100.0 AS DECIMAL(19,2)) AS variance_usd,
       CAST(100.0 * SUM(variance_cents) / NULLIF(SUM(budget_cents),0) AS DECIMAL(9,2)) AS variance_pct
FROM dbo.vw_finance_monthly_variance
WHERE fiscal_year = @FiscalYear AND fiscal_month_index <= @FiscalMonthThrough
GROUP BY department_name, expense_class
ORDER BY department_name, expense_class;

-- Monthly budget / actual trend for executive visuals.
SELECT month_start, fiscal_month_index,
       CAST(SUM(budget_cents) / 100.0 AS DECIMAL(19,2)) AS budget_usd,
       CAST(SUM(actual_cents) / 100.0 AS DECIMAL(19,2)) AS actual_usd,
       CAST(SUM(variance_cents) / 100.0 AS DECIMAL(19,2)) AS variance_usd
FROM dbo.vw_finance_monthly_variance
WHERE fiscal_year = @FiscalYear AND fiscal_month_index <= @FiscalMonthThrough
GROUP BY month_start, fiscal_month_index
ORDER BY fiscal_month_index;

-- Row-count and raw-ledger reconciliation checks (both deltas must be zero).
SELECT
    (SELECT SUM(actual_cents) FROM dbo.fact_actual)
    - (SELECT SUM(actual_cents) FROM dbo.vw_finance_monthly_variance)
    AS unmatched_actual_cents,
    (SELECT SUM(budget_cents) FROM dbo.fact_budget)
    - (SELECT SUM(budget_cents) FROM dbo.vw_finance_monthly_variance)
    AS unmatched_budget_cents;
