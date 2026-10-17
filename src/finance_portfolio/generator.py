"""Deterministic, fictional finance data; no employer records or identifiers."""
import csv
import random
from calendar import monthrange
from datetime import date, timedelta
from pathlib import Path

SEED = 42
DEPARTMENTS = [
    ("D001", "Fleet Services", "Operations"),
    ("D002", "Facilities", "Operations"),
    ("D003", "Information Technology", "Technology"),
    ("D004", "Customer Experience", "Service"),
    ("D005", "Administration", "Corporate"),
    ("D006", "Procurement", "Corporate"),
]
GL_ACCOUNTS = [
    ("5100", "Base Salaries", "Labor", 162000),
    ("5110", "Overtime", "Labor", 23000),
    ("5120", "Employee Benefits", "Labor", 41000),
    ("6100", "Parts and Materials", "Non-Labor", 49000),
    ("6110", "Fuel and Utilities", "Non-Labor", 54000),
    ("6120", "Contracted Services", "Non-Labor", 62000),
    ("6130", "Software and Licenses", "Non-Labor", 18000),
    ("6140", "Training and Travel", "Non-Labor", 8000),
]
DEPT_FACTORS = [1.4, 1.15, 1.0, 0.8, 0.65, 0.9]


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def month_starts(start_year=2024, start_month=10, count=24):
    for offset in range(count):
        month_number = (start_month - 1) + offset
        yield date(start_year + month_number // 12, month_number % 12 + 1, 1)


def fiscal_fields(value: date) -> dict:
    fy = value.year + (value.month >= 10)
    fiscal_month = ((value.month - 10) % 12) + 1
    return {
        "fiscal_year": fy,
        "fiscal_year_label": f"FY{fy}",
        "fiscal_month_index": fiscal_month,
        "fiscal_quarter": ((fiscal_month - 1) // 3) + 1,
        "month_start": value.replace(day=1).isoformat(),
    }


def generate(root: Path) -> dict:
    """Rebuild *only synthetic source CSVs* consistently on every execution."""
    rng = random.Random(SEED)
    output = root / "data" / "synthetic"
    output.mkdir(parents=True, exist_ok=True)
    dept_rows = [{"department_id": d, "department_name": n, "business_unit": u}
                 for d, n, u in DEPARTMENTS]
    gl_rows = [{"gl_account_id": g, "gl_account_name": n, "expense_class": c}
               for g, n, c, _ in GL_ACCOUNTS]
    write_csv(output / "departments.csv", list(dept_rows[0]), dept_rows)
    write_csv(output / "gl_accounts.csv", list(gl_rows[0]), gl_rows)

    calendar_rows = []
    cursor = date(2024, 10, 1)
    while cursor <= date(2026, 9, 30):
        calendar_rows.append({"date": cursor.isoformat(), **fiscal_fields(cursor),
                              "calendar_year": cursor.year, "calendar_month": cursor.month})
        cursor += timedelta(days=1)
    write_csv(output / "fiscal_calendar.csv", list(calendar_rows[0]), calendar_rows)

    budgets, actuals = [], []
    for month in month_starts():
        quarter = ((month.month - 10) % 12) // 3
        for dept_index, (dept_id, _, _) in enumerate(DEPARTMENTS):
            for gl_id, gl_name, expense_class, base_dollars in GL_ACCOUNTS:
                # Seasonality, planned annual escalation, and department mix are entirely fictional.
                seasonal = 1 + (0.09 if quarter == 3 else 0) + (0.05 if month.month == 12 else 0)
                escalation = 1.035 if month.year >= 2026 else 1.0
                budget_cents = round(base_dollars * 100 * DEPT_FACTORS[dept_index]
                                     * seasonal * escalation)
                budgets.append({"budget_id": f"B{len(budgets) + 1:05d}",
                                "month_start": month.isoformat(), "department_id": dept_id,
                                "gl_account_id": gl_id, "budget_cents": budget_cents})
                # Actual spend is partitioned into 2-4 transaction lines, preserving exact cents.
                deviation = rng.uniform(-0.14, 0.14)
                if gl_id == "5110" and month.month in (6, 7, 8):
                    deviation += 0.16  # planned example of overtime budget pressure
                if gl_id == "6110" and month.month in (1, 2):
                    deviation += 0.11
                actual_total = max(0, round(budget_cents * (1 + deviation)))
                count = rng.randint(2, 4)
                # Integer allocation avoids rounding leakage.
                cuts = sorted(rng.sample(range(1, actual_total), count - 1))
                pieces = [b - a for a, b in zip([0] + cuts, cuts + [actual_total])]
                days = monthrange(month.year, month.month)[1]
                for piece in pieces:
                    tx_date = month.replace(day=rng.randint(1, days)).isoformat()
                    actuals.append({"transaction_id": f"T{len(actuals) + 1:06d}",
                                    "transaction_date": tx_date, "department_id": dept_id,
                                    "gl_account_id": gl_id, "actual_cents": piece,
                                    "reference": f"SYN-{len(actuals) + 1:06d}"})

    write_csv(output / "budgets.csv", list(budgets[0]), budgets)
    write_csv(output / "actuals.csv", list(actuals[0]), actuals)
    return {"departments": len(dept_rows), "gl_accounts": len(gl_rows),
            "calendar_days": len(calendar_rows), "budget_lines": len(budgets),
            "actual_transactions": len(actuals)}
