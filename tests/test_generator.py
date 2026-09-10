import json
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

from dailybread.generator import DailyBreadEntry, generate_entry


ROOT = Path(__file__).resolve().parents[1]


class GeneratorTests(unittest.TestCase):
    def test_generate_entry_is_deterministic_for_current_static_layers(self):
        target = date(2025, 2, 25)
        self.assertEqual(generate_entry(target), generate_entry(target))

    def test_entry_structure(self):
        entry = generate_entry(date(2024, 12, 9))
        self.assertIsInstance(entry, DailyBreadEntry)
        self.assertGreaterEqual(len(entry.observations), 1)
        self.assertGreaterEqual(len(entry.astrological_factors), 1)
        self.assertIsNotNone(entry.primary_theme)
        self.assertEqual(len(entry.citations), 9)
        self.assertTrue(all(citation.evidence_class == "comparative" for citation in entry.citations))

    def test_serialized_entry_contains_iso_date(self):
        entry = generate_entry(date(2025, 2, 25))
        self.assertEqual(entry.to_dict()["target_date"], "2025-02-25")


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "dailybread", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_text_output_contains_requested_date(self):
        result = self.run_cli("--date", "2025-02-25")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Daily Bread + Nine for Tuesday, February 25, 2025", result.stdout)
        self.assertIn("Observed Sky", result.stdout)
        self.assertIn("Astrological Lens", result.stdout)
        self.assertIn("The Plus Nine", result.stdout)

    def test_json_output_contains_nine_citations(self):
        result = self.run_cli("--date", "2025-02-25", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["target_date"], "2025-02-25")
        self.assertEqual(len(payload["citations"]), 9)

    def test_invalid_calendar_date_is_rejected(self):
        result = self.run_cli("--date", "2025-02-30")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Use YYYY-MM-DD", result.stderr)

    def test_noncanonical_date_is_rejected(self):
        result = self.run_cli("--date", "2025-2-5")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Use YYYY-MM-DD", result.stderr)


if __name__ == "__main__":
    unittest.main()
