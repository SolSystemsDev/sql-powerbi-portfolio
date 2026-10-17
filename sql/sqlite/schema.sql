-- SQLite execution target for portable Codespaces demos. Currency stored as whole cents.
PRAGMA foreign_keys = ON;
DROP VIEW IF EXISTS vw_monthly_variance;
DROP TABLE IF EXISTS fact_actual;
DROP TABLE IF EXISTS fact_budget;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_gl_account;
DROP TABLE IF EXISTS dim_department;

CREATE TABLE dim_department (
    department_id TEXT PRIMARY KEY,
    department_name TEXT NOT NULL UNIQUE,
    business_unit TEXT NOT NULL
);
CREATE TABLE dim_gl_account (
    gl_account_id TEXT PRIMARY KEY,
    gl_account_name TEXT NOT NULL UNIQUE,
    expense_class TEXT NOT NULL CHECK (expense_class IN ('Labor', 'Non-Labor'))
);
CREATE TABLE dim_date (
    date TEXT PRIMARY KEY,
    fiscal_year INTEGER NOT NULL,
    fiscal_year_label TEXT NOT NULL,
    fiscal_month_index INTEGER NOT NULL CHECK(fiscal_month_index BETWEEN 1 AND 12),
    fiscal_quarter INTEGER NOT NULL CHECK(fiscal_quarter BETWEEN 1 AND 4),
    month_start TEXT NOT NULL,
    calendar_year INTEGER NOT NULL,
    calendar_month INTEGER NOT NULL
);
CREATE TABLE fact_budget (
    budget_id TEXT PRIMARY KEY,
    month_start TEXT NOT NULL REFERENCES dim_date(date),
    department_id TEXT NOT NULL REFERENCES dim_department(department_id),
    gl_account_id TEXT NOT NULL REFERENCES dim_gl_account(gl_account_id),
    budget_cents INTEGER NOT NULL CHECK(budget_cents >= 0),
    UNIQUE(month_start, department_id, gl_account_id)
);
CREATE TABLE fact_actual (
    transaction_id TEXT PRIMARY KEY,
    transaction_date TEXT NOT NULL REFERENCES dim_date(date),
    department_id TEXT NOT NULL REFERENCES dim_department(department_id),
    gl_account_id TEXT NOT NULL REFERENCES dim_gl_account(gl_account_id),
    actual_cents INTEGER NOT NULL CHECK(actual_cents >= 0),
    reference TEXT NOT NULL UNIQUE
);
CREATE INDEX idx_actual_date_dept_gl ON fact_actual(transaction_date, department_id, gl_account_id);
CREATE INDEX idx_budget_month_dept_gl ON fact_budget(month_start, department_id, gl_account_id);
CREATE INDEX idx_date_fiscal ON dim_date(fiscal_year, fiscal_month_index);

-- Variance convention: actual - budget; POSITIVE means unfavorable overspend.
CREATE VIEW vw_monthly_variance AS
WITH actual_monthly AS (
    SELECT substr(transaction_date, 1, 7) || '-01' AS month_start,
           department_id, gl_account_id, SUM(actual_cents) AS actual_cents
    FROM fact_actual
    GROUP BY substr(transaction_date, 1, 7), department_id, gl_account_id
)
SELECT b.month_start, dd.fiscal_year, dd.fiscal_month_index,
       d.department_id, d.department_name, d.business_unit,
       g.gl_account_id, g.gl_account_name, g.expense_class,
       b.budget_cents, COALESCE(a.actual_cents, 0) AS actual_cents,
       COALESCE(a.actual_cents, 0) - b.budget_cents AS variance_cents
FROM fact_budget b
JOIN dim_date dd ON dd.date = b.month_start
JOIN dim_department d ON d.department_id = b.department_id
JOIN dim_gl_account g ON g.gl_account_id = b.gl_account_id
LEFT JOIN actual_monthly a ON a.month_start = b.month_start
    AND a.department_id = b.department_id AND a.gl_account_id = b.gl_account_id;
