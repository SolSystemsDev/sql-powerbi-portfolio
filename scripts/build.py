#!/usr/bin/env python3
"""One command: synthesize -> load SQL -> validate -> aggregate -> render."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from finance_portfolio.generator import generate
from finance_portfolio.pipeline import assert_integrity, export_report, load_database, report_data
from finance_portfolio.rendering import render_html


def main():
    counts = generate(ROOT)
    conn = load_database(ROOT)
    try:
        assert_integrity(conn)
        result = report_data(conn, 2026, 12)
    finally:
        conn.close()
    export_report(ROOT, result)
    render_html(ROOT, result)
    print("BUILD SUCCESS | Entirely synthetic financial data")
    print("Inputs:", json.dumps(counts, sort_keys=True))
    print(f"FY{result['fiscal_year']} budget: ${result['budget_cents'] / 100:,.2f}")
    print(f"FY{result['fiscal_year']} actual: ${result['actual_cents'] / 100:,.2f}")
    print(f"FY{result['fiscal_year']} variance (actual - budget): ${result['variance_cents'] / 100:,.2f}")
    print("View: reports/executive_dashboard.html")


if __name__ == "__main__":
    main()
