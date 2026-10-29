import csv
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from maintenance_sql.core import QUERIES, connect, load, parameters, query
from maintenance_sql.report import run
from maintenance_sql.synthetic import generate

START = "2025-01-01 08:00:00"
END = "2025-01-01 16:00:00"


def fixture():
    return {
        "assets": [(1, "Motor", "A", 1), (2, "Bomba", "A", 2), (3, "Reserva", "B", 3)],
        "work_orders": [
            (1, 1, "corrective", 1, START, END, "2025-01-01 10:00:00", None),
            (2, 1, "corrective", 2, START, END, None, None),
            (3, 1, "corrective", 1, START, END, "2025-01-01 17:00:00", None),
            (4, 2, "preventive", 3, START, END, None, END),
            (5, 2, "preventive", 3, START, END, None, "2025-01-01 17:00:00"),
            (6, 2, "preventive", 3, END, END, None, None),
        ],
        "failures": [
            (1, 1, 1, START, "2025-01-01 10:00:00", "electrical"),
            (2, 1, 2, START, None, "mechanical"),
            (3, 1, 3, START, "2025-01-01 17:00:00", "electrical"),
        ],
        "downtime": [
            (1, 1, START, "2025-01-01 12:00:00", "failure"),
            (2, 1, "2025-01-01 09:00:00", "2025-01-01 10:00:00", "utility"),
            (3, 1, "2025-01-01 11:00:00", "2025-01-01 13:00:00", "failure"),
            (4, 1, "2025-01-01 07:00:00", START, "planned"),
            (5, 2, "2025-01-01 15:00:00", None, "failure"),
        ],
        "shifts": [(1, 1, START, END), (2, 2, START, END)],
        "parts": [(1, "Bearing"), (2, "Sensor")],
        "part_usage": [
            (1, 1, 1, START, 2, 1234),
            (2, 1, 1, "2025-01-01 09:00:00", 1, 1500),
            (3, 1, 2, END, 10, 99999),
        ],
    }


class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.db = connect()
        load(self.db, fixture())

    def tearDown(self):
        self.db.close()

    def result(self, name):
        return query(self.db, name, START, END)

    def test_nested_overlapping_touching_and_open_stops(self):
        rows = self.result("01_downtime")
        self.assertEqual([r["stop_hours"] for r in rows], [5.0, 1.0, 0.0])
        self.assertEqual(rows[-1]["cumulative_pct"], 100.0)

    def test_restore_cohort_excludes_open_and_future_restorations(self):
        row = self.result("02_mttr")[0]
        self.assertEqual(
            (row["failures"], row["restored"], row["censored"], row["mttr_hours"]),
            (3, 1, 2, 2.0),
        )
        self.assertIsNone(self.result("02_mttr")[-1]["mttr_hours"])

    def test_backlog_reconstructs_historical_snapshot(self):
        ids = {r["order_id"] for r in self.result("03_backlog")}
        self.assertEqual(ids, {2, 3, 5})

    def test_parts_keep_transaction_price_and_do_not_fan_out(self):
        rows = self.result("04_parts")
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["units"], rows[0]["cost_cents"]), (3, 3968))

    def test_scheduled_intersection_and_unknown_schedule(self):
        rows = {r["asset_id"]: r for r in self.result("05_shifts")}
        self.assertEqual(rows[1]["scheduled_availability_pct"], 37.5)
        self.assertEqual(rows[2]["scheduled_availability_pct"], 87.5)
        self.assertIsNone(rows[3]["scheduled_availability_pct"])

    def test_no_stops_is_zero_share_unknown(self):
        self.db.execute("DELETE FROM downtime")
        rows = self.result("01_downtime")
        self.assertEqual(rows[0]["stop_hours"], 0)
        self.assertIsNone(rows[0]["share_pct"])

    def test_invalid_timestamp_rejected_insert_and_update(self):
        for value in ("2025-02-30 09:00:00", "2025-01-01T09:00:00", "nonsense"):
            with self.subTest(value=value), self.assertRaises(sqlite3.IntegrityError):
                self.db.execute(
                    "UPDATE downtime SET start_at=? WHERE event_id=1", (value,)
                )

    def test_overlap_shift_rejected_insert_and_update(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO shifts VALUES(4,1,'2025-01-01 09:00:00','2025-01-01 10:00:00')"
            )
        self.db.execute(
            "INSERT INTO shifts VALUES(5,1,'2025-01-01 16:00:00','2025-01-01 20:00:00')"
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "UPDATE shifts SET start_at='2025-01-01 15:00:00' WHERE shift_id=5"
            )

    def test_cross_asset_failure_and_negative_cost_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO failures VALUES(7,2,1,?,NULL,'test')", (START,)
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE part_usage SET unit_cost_cents=-1 WHERE usage_id=1")

    def test_invalid_window(self):
        for a, b in ((END, START), (START, START), ("invalid", END)):
            with self.assertRaises(ValueError):
                parameters(a, b)

    def test_empty_period_does_not_fabricate_availability(self):
        rows = query(self.db, "05_shifts", "2024-01-01 00:00:00", "2024-02-01 00:00:00")
        self.assertTrue(all(r["scheduled_availability_pct"] is None for r in rows))

    def test_load_rolls_back_whole_scenario(self):
        db = connect()
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                load(
                    db,
                    {
                        "assets": [(1, "Asset", "A", 1)],
                        "parts": [(1, "Duplicate"), (2, "Duplicate")],
                    },
                )
            self.assertEqual(db.execute("SELECT COUNT(*) FROM assets").fetchone()[0], 0)
        finally:
            db.close()

    def test_reproducible_data_and_report_exports(self):
        self.assertEqual(generate(42), generate(42))
        self.assertNotEqual(generate(42), generate(43))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            run(path)
            metrics = json.loads((path / "metrics.json").read_text(encoding="utf-8"))
            for name in QUERIES:
                with (path / (name + ".csv")).open(encoding="utf-8", newline="") as f:
                    self.assertEqual(
                        len(list(csv.DictReader(f))), len(metrics["results"][name])
                    )
            self.assertIn("Datos", (path / "RESULTS.md").read_text(encoding="utf-8"))
            hashes = (path / "manifest.json").read_text()
            run(path)
            self.assertEqual((path / "manifest.json").read_text(), hashes)


if __name__ == "__main__":
    unittest.main()
