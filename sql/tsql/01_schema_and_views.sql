/*
SQL Server reference implementation (T-SQL). Not executed or engine-validated by this
SQLite-only v0.1 CI; adapt schema/import types to target SQL Server environment.
Do not run against production databases. Use a disposable development database.
Amounts are signed BIGINT cents; this synthetic example has expenses only.
*/
IF OBJECT_ID('dbo.vw_finance_monthly_variance', 'V') IS NOT NULL
    DROP VIEW dbo.vw_finance_monthly_variance;
GO
DROP TABLE IF EXISTS dbo.fact_actual;
DROP TABLE IF EXISTS dbo.fact_budget;
DROP TABLE IF EXISTS dbo.dim_date;
DROP TABLE IF EXISTS dbo.dim_gl_account;
DROP TABLE IF EXISTS dbo.dim_department;
GO
CREATE TABLE dbo.dim_department (
    department_id VARCHAR(5) NOT NULL PRIMARY KEY,
    department_name NVARCHAR(100) NOT NULL UNIQUE,
    business_unit NVARCHAR(80) NOT NULL
);
CREATE TABLE dbo.dim_gl_account (
    gl_account_id VARCHAR(10) NOT NULL PRIMARY KEY,
    gl_account_name NVARCHAR(100) NOT NULL UNIQUE,
    expense_class VARCHAR(9) NOT NULL CHECK (expense_class IN ('Labor','Non-Labor'))
);
CREATE TABLE dbo.dim_date (
    [date] DATE NOT NULL PRIMARY KEY,
    fiscal_year INT NOT NULL,
    fiscal_year_label VARCHAR(8) NOT NULL,
    fiscal_month_index TINYINT NOT NULL CHECK (fiscal_month_index BETWEEN 1 AND 12),
    fiscal_quarter TINYINT NOT NULL CHECK (fiscal_quarter BETWEEN 1 AND 4),
    month_start DATE NOT NULL,
    calendar_year INT NOT NULL,
    calendar_month TINYINT NOT NULL
);
CREATE TABLE dbo.fact_budget (
    budget_id VARCHAR(16) NOT NULL PRIMARY KEY,
    month_start DATE NOT NULL REFERENCES dbo.dim_date([date]),
    department_id VARCHAR(5) NOT NULL REFERENCES dbo.dim_department(department_id),
    gl_account_id VARCHAR(10) NOT NULL REFERENCES dbo.dim_gl_account(gl_account_id),
    budget_cents BIGINT NOT NULL CHECK (budget_cents >= 0),
    CONSTRAINT uq_budget_grain UNIQUE(month_start, department_id, gl_account_id)
);
CREATE TABLE dbo.fact_actual (
    transaction_id VARCHAR(16) NOT NULL PRIMARY KEY,
    transaction_date DATE NOT NULL REFERENCES dbo.dim_date([date]),
    department_id VARCHAR(5) NOT NULL REFERENCES dbo.dim_department(department_id),
    gl_account_id VARCHAR(10) NOT NULL REFERENCES dbo.dim_gl_account(gl_account_id),
    actual_cents BIGINT NOT NULL CHECK (actual_cents >= 0),
    reference VARCHAR(24) NOT NULL UNIQUE
);
CREATE INDEX ix_actual_date_dept_gl ON dbo.fact_actual(transaction_date,department_id,gl_account_id)
    INCLUDE(actual_cents);
CREATE INDEX ix_budget_month_dept_gl ON dbo.fact_budget(month_start,department_id,gl_account_id)
    INCLUDE(budget_cents);
GO
CREATE OR ALTER VIEW dbo.vw_finance_monthly_variance
AS
WITH actual_monthly AS (
    SELECT DATEFROMPARTS(YEAR(a.transaction_date), MONTH(a.transaction_date), 1) AS month_start,
           a.department_id, a.gl_account_id, SUM(a.actual_cents) AS actual_cents
    FROM dbo.fact_actual AS a
    GROUP BY DATEFROMPARTS(YEAR(a.transaction_date), MONTH(a.transaction_date), 1),
             a.department_id, a.gl_account_id
)
SELECT b.month_start, cal.fiscal_year, cal.fiscal_month_index,
       dept.department_id, dept.department_name, dept.business_unit,
       gl.gl_account_id, gl.gl_account_name, gl.expense_class,
       b.budget_cents, COALESCE(act.actual_cents, CONVERT(BIGINT,0)) AS actual_cents,
       COALESCE(act.actual_cents, CONVERT(BIGINT,0)) - b.budget_cents AS variance_cents
FROM dbo.fact_budget AS b
JOIN dbo.dim_date AS cal ON cal.[date] = b.month_start
JOIN dbo.dim_department AS dept ON dept.department_id = b.department_id
JOIN dbo.dim_gl_account AS gl ON gl.gl_account_id = b.gl_account_id
LEFT JOIN actual_monthly AS act ON act.month_start = b.month_start
    AND act.department_id = b.department_id AND act.gl_account_id = b.gl_account_id;
GO
