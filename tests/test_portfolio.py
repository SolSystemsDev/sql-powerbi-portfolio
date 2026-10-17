"""Integration + fiscal-calendar + reconciliation tests. No third-party packages."""
import csv
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from finance_portfolio.generator import fiscal_fields, generate
from finance_portfolio.pipeline import assert_integrity, load_database, report_data
from datetime import date


class FiscalCalendarTests(unittest.TestCase):
    def test_october_rollover(self):
        self.assertEqual((fiscal_fields(date(2025, 9, 30))["fiscal_year"],
                          fiscal_fields(date(2025, 9, 30))["fiscal_month_index"]), (2025, 12))
        self.assertEqual((fiscal_fields(date(2025, 10, 1))["fiscal_year"],
                          fiscal_fields(date(2025, 10, 1))["fiscal_month_index"]), (2026, 1))

    def test_january_and_september_positions(self):
        self.assertEqual(fiscal_fields(date(2026, 1, 15))["fiscal_month_index"], 4)
        self.assertEqual(fiscal_fields(date(2026, 9, 30))["fiscal_month_index"], 12)
        self.assertEqual(fiscal_fields(date(2026, 7, 1))["fiscal_quarter"], 4)


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        (cls.root / "sql" / "sqlite").mkdir(parents=True)
        (cls.root / "sql" / "sqlite" / "schema.sql").write_text(
            (ROOT / "sql" / "sqlite" / "schema.sql").read_text(encoding="utf-8"), encoding="utf-8")
        cls.counts = generate(cls.root)
        cls.conn = load_database(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        cls.tmp.cleanup()

    def test_expected_grain(self):
        self.assertEqual(self.counts["budget_lines"], 24 * 6 * 8)
        self.assertEqual(self.counts["calendar_days"], 730)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM vw_monthly_variance").fetchone()[0], 1152)

    def test_reconciliation(self):
        assert_integrity(self.conn)
        raw_actual = self.conn.execute("SELECT SUM(actual_cents) FROM fact_actual").fetchone()[0]
        mapped_actual = self.conn.execute("SELECT SUM(actual_cents) FROM vw_monthly_variance").fetchone()[0]
        self.assertEqual(raw_actual, mapped_actual)

    def test_fiscal_ytd_cumulative(self):
        full = report_data(self.conn, 2026, 12)
        first_half = report_data(self.conn, 2026, 6)
        remaining = self.conn.execute("""SELECT SUM(actual_cents) FROM vw_monthly_variance
            WHERE fiscal_year = 2026 AND fiscal_month_index BETWEEN 7 AND 12""").fetchone()[0]
        self.assertEqual(full["actual_cents"], first_half["actual_cents"] + remaining)
        self.assertEqual(first_half["month_count"], 6)
        self.assertEqual(full["month_count"], 12)

    def test_classes_and_dimensions_total(self):
        report = report_data(self.conn, 2026, 12)
        self.assertEqual({r["expense_class"] for r in report["classifications"]},
                         {"Labor", "Non-Labor"})
        self.assertEqual(sum(r["budget_cents"] for r in report["departments"]),
                         report["budget_cents"])
        self.assertEqual(sum(r["variance_cents"] for r in report["gl_accounts"]),
                         report["variance_cents"])

    def test_positive_variance_means_over_budget(self):
        report = report_data(self.conn, 2026, 12)
        self.assertEqual(report["variance_cents"],
                         report["actual_cents"] - report["budget_cents"])

    def test_fiscal_year_distinction(self):
        prev = report_data(self.conn, 2025, 12)
        now = report_data(self.conn, 2026, 12)
        self.assertNotEqual(prev["budget_cents"], now["budget_cents"])

    def test_synthetic_source_determinism(self):
        source_path = self.root / "data" / "synthetic" / "actuals.csv"
        before = source_path.read_bytes()
        generate(self.root)
        self.assertEqual(before, source_path.read_bytes())

    def test_foreign_keys_reject_bad_date(self):
        with self.assertRaises(sqlite3.IntegrityError):
            with self.conn:
                self.conn.execute("""INSERT INTO fact_actual
                    (transaction_id,transaction_date,department_id,gl_account_id,actual_cents,reference)
                    VALUES ('BAD','2030-01-01','D001','5100',1,'BAD')""")

    def test_invalid_ytd_month(self):
        with self.assertRaises(ValueError):
            report_data(self.conn, 2026, 13)


if __name__ == "__main__":
    unittest.main()
