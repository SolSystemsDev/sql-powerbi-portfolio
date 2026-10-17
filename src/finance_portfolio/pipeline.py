"""SQLite ETL, financial aggregations and integrity controls (Python stdlib only)."""
import csv
import json
import sqlite3
from pathlib import Path

TABLES = {
    "dim_department": ("departments.csv", ["department_id", "department_name", "business_unit"]),
    "dim_gl_account": ("gl_accounts.csv", ["gl_account_id", "gl_account_name", "expense_class"]),
    "dim_date": ("fiscal_calendar.csv", ["date", "fiscal_year", "fiscal_year_label",
                 "fiscal_month_index", "fiscal_quarter", "month_start", "calendar_year", "calendar_month"]),
    "fact_budget": ("budgets.csv", ["budget_id", "month_start", "department_id", "gl_account_id", "budget_cents"]),
    "fact_actual": ("actuals.csv", ["transaction_id", "transaction_date", "department_id",
                     "gl_account_id", "actual_cents", "reference"]),
}
INT_FIELDS = {"fiscal_year", "fiscal_month_index", "fiscal_quarter", "calendar_year",
              "calendar_month", "budget_cents", "actual_cents"}


def fetch_all_dict(conn: sqlite3.Connection, sql: str, params=()):
    cursor = conn.execute(sql, params)
    return [dict(row) for row in cursor.fetchall()]


def dollars(cents: int) -> str:
    return f"{cents / 100:.2f}"


def load_database(root: Path) -> sqlite3.Connection:
    db = root / "data" / "processed" / "finance_analytics.db"
    db.parent.mkdir(parents=True, exist_ok=True)
    if db.exists():
        db.unlink()
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript((root / "sql" / "sqlite" / "schema.sql").read_text(encoding="utf-8"))
    source = root / "data" / "synthetic"
    try:
        with conn:
            for table, (filename, fields) in TABLES.items():
                with (source / filename).open(newline="", encoding="utf-8") as stream:
                    reader = csv.DictReader(stream)
                    if reader.fieldnames != fields:
                        raise ValueError(f"Unexpected columns in {filename}: {reader.fieldnames}")
                    records = []
                    for row in reader:
                        records.append(tuple(int(row[f]) if f in INT_FIELDS else row[f] for f in fields))
                placeholders = ",".join("?" for _ in fields)
                conn.executemany(f"INSERT INTO {table} ({','.join(fields)}) VALUES ({placeholders})", records)
        return conn
    except Exception:
        conn.close()
        raise


def assert_integrity(conn):
    issues = conn.execute("PRAGMA foreign_key_check").fetchall()
    if issues:
        raise ValueError(f"Foreign-key validation failed: {issues}")
    checks = {
        "missing_actual_from_view": """
            SELECT (SELECT COALESCE(SUM(actual_cents),0) FROM fact_actual)
                 - (SELECT COALESCE(SUM(actual_cents),0) FROM vw_monthly_variance)""",
        "missing_budget_from_view": """
            SELECT (SELECT COALESCE(SUM(budget_cents),0) FROM fact_budget)
                 - (SELECT COALESCE(SUM(budget_cents),0) FROM vw_monthly_variance)""",
        "duplicated_budget_grain": """
            SELECT COUNT(*) FROM (SELECT month_start, department_id, gl_account_id,
            COUNT(*) AS n FROM vw_monthly_variance GROUP BY 1,2,3 HAVING n > 1)""",
        "uncategorized_expenses": "SELECT COUNT(*) FROM dim_gl_account WHERE expense_class NOT IN ('Labor','Non-Labor')",
    }
    for name, sql in checks.items():
        result = conn.execute(sql).fetchone()[0]
        if result != 0:
            raise ValueError(f"Quality gate failed: {name} = {result}")


def write_rows(path: Path, fields: list[str], rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def report_data(conn: sqlite3.Connection, fiscal_year=2026, through_fiscal_month=12) -> dict:
    if not 1 <= through_fiscal_month <= 12:
        raise ValueError("through_fiscal_month must be between 1 and 12")
    where = "WHERE fiscal_year = ? AND fiscal_month_index <= ?"
    params = (fiscal_year, through_fiscal_month)
    grain = fetch_all_dict(conn, f"SELECT * FROM vw_monthly_variance {where} ORDER BY fiscal_month_index, department_id, gl_account_id", params)
    if not grain:
        raise ValueError(f"No financial data for FY{fiscal_year}")
    monthly = fetch_all_dict(conn, f"""
        SELECT month_start, fiscal_year, fiscal_month_index,
               SUM(budget_cents) AS budget_cents, SUM(actual_cents) AS actual_cents,
               SUM(variance_cents) AS variance_cents
        FROM vw_monthly_variance {where}
        GROUP BY month_start, fiscal_year, fiscal_month_index ORDER BY fiscal_month_index""", params)
    dept = fetch_all_dict(conn, f"""
        SELECT department_id, department_name, SUM(budget_cents) AS budget_cents,
               SUM(actual_cents) AS actual_cents, SUM(variance_cents) AS variance_cents
        FROM vw_monthly_variance {where}
        GROUP BY department_id, department_name ORDER BY variance_cents DESC""", params)
    gl = fetch_all_dict(conn, f"""
        SELECT gl_account_id, gl_account_name, expense_class,
               SUM(budget_cents) AS budget_cents, SUM(actual_cents) AS actual_cents,
               SUM(variance_cents) AS variance_cents
        FROM vw_monthly_variance {where}
        GROUP BY gl_account_id, gl_account_name, expense_class ORDER BY variance_cents DESC""", params)
    classifications = fetch_all_dict(conn, f"""
        SELECT expense_class, SUM(budget_cents) AS budget_cents,
               SUM(actual_cents) AS actual_cents, SUM(variance_cents) AS variance_cents
        FROM vw_monthly_variance {where}
        GROUP BY expense_class ORDER BY expense_class""", params)
    exceptions = [row for row in grain if row["variance_cents"] >= 500_000
                  and row["variance_cents"] * 100 >= row["budget_cents"] * 20]
    result = {"fiscal_year": fiscal_year, "through_fiscal_month": through_fiscal_month,
              "month_count": len(monthly), "grain": grain, "monthly": monthly,
              "departments": dept, "gl_accounts": gl, "classifications": classifications,
              "exceptions": exceptions}
    result["budget_cents"] = sum(row["budget_cents"] for row in monthly)
    result["actual_cents"] = sum(row["actual_cents"] for row in monthly)
    result["variance_cents"] = result["actual_cents"] - result["budget_cents"]
    result["variance_pct"] = (result["variance_cents"] / result["budget_cents"] * 100
                              if result["budget_cents"] else None)
    assert sum(r["actual_cents"] for r in dept) == result["actual_cents"]
    assert sum(r["actual_cents"] for r in gl) == result["actual_cents"]
    assert sum(r["actual_cents"] for r in classifications) == result["actual_cents"]
    return result


def export_report(root: Path, result: dict) -> None:
    out = root / "data" / "processed"
    def convert(row, fields):
        return {name.replace("_cents", "_usd"): dollars(row[name]) if name.endswith("_cents")
                else row[name] for name in fields}
    outputs = {
        "monthly_variance.csv": (result["monthly"], ["month_start", "fiscal_year",
           "fiscal_month_index", "budget_cents", "actual_cents", "variance_cents"]),
        "department_summary.csv": (result["departments"], ["department_id", "department_name",
           "budget_cents", "actual_cents", "variance_cents"]),
        "gl_summary.csv": (result["gl_accounts"], ["gl_account_id", "gl_account_name",
           "expense_class", "budget_cents", "actual_cents", "variance_cents"]),
        "monthly_detail.csv": (result["grain"], ["month_start", "fiscal_year",
           "fiscal_month_index", "department_id", "department_name", "business_unit",
           "gl_account_id", "gl_account_name", "expense_class", "budget_cents", "actual_cents", "variance_cents"]),
        "unfavorable_exceptions.csv": (result["exceptions"], ["month_start", "department_name",
           "gl_account_name", "budget_cents", "actual_cents", "variance_cents"]),
    }
    for filename, (rows, fields) in outputs.items():
        transformed = [convert(row, fields) for row in rows]
        new_fields = [k.replace("_cents", "_usd") for k in fields]
        write_rows(out / filename, new_fields, transformed)
    headline = {"fiscal_year": result["fiscal_year"],
                "through_fiscal_month": result["through_fiscal_month"],
                "budget_usd": dollars(result["budget_cents"]),
                "actual_usd": dollars(result["actual_cents"]),
                "variance_usd": dollars(result["variance_cents"]),
                "variance_pct": round(result["variance_pct"], 2),
                "variance_definition": "Actual - Budget; positive is unfavorable for expenses",
                "synthetic_data": True}
    (out / "executive_kpis.json").write_text(json.dumps(headline, indent=2) + "\n", encoding="utf-8")
