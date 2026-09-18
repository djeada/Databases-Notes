"""Offline checks for safety guards and persistence invariants (no DB needed)."""

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock

try:
    import psycopg2
except ImportError:
    psycopg2 = types.ModuleType("psycopg2")
    psycopg2.Error = type("FakePsycopgError", (Exception,), {})
    sys.modules["psycopg2"] = psycopg2

SCRIPT = Path(__file__).resolve().parents[1] / "lab.py"
spec = importlib.util.spec_from_file_location("acid_escape_room_lab", SCRIPT)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class SafetyAndInvariantTests(unittest.TestCase):
    def test_worker_limits(self):
        for size in (2, 8, 16):
            lab.validate_workers(size)
        for size in (0, 1, 17, 100):
            with self.assertRaises(ValueError):
                lab.validate_workers(size)

    def test_failure_check_is_not_python_assert(self):
        with self.assertRaises(AssertionError):
            lab.require(False, "bad outcome")
        lab.require(True, "works")

    def test_durability_requires_all_good_and_no_bad(self):
        connection = MagicMock()
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = [("good", 1), ("good", 2)]
        self.assertEqual(lab.verify_receipts(connection, 2),
                         {"good_persisted": 2, "bad_persisted": 0})
        cursor.fetchall.return_value = [("good", 1)]
        with self.assertRaises(AssertionError):
            lab.verify_receipts(connection, 2)
        cursor.fetchall.return_value = [("good", 1), ("good", 2), ("bad", 1)]
        with self.assertRaises(AssertionError):
            lab.verify_receipts(connection, 2)

    def test_refuses_non_lab_database(self):
        connection = MagicMock()
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = ("production",)
        with self.assertRaisesRegex(AssertionError, "Refusing"):
            lab.guard_database(connection)
        cursor.fetchone.return_value = ("acid_lab",)
        lab.guard_database(connection)
        connection.rollback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
