import json
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

from dailybread.generator import DailyBreadEntry, generate_entry


ROOT = Path(__file__).resolve().parents[1]


class GeneratorTests(unittest.TestCase):
    def test_generate_entry_is_deterministic(self):
        target = date(2025, 2, 25)
        self.assertEqual(generate_entry(target), generate_entry(target))

    def test_entry_structure(self):
        entry = generate_entry(date(2024, 12, 9))
        self.assertIsInstance(entry, DailyBreadEntry)
        self.assertEqual(set(entry.cosmic_focus), {"title", "summary", "connection"})
        self.assertEqual(len(entry.reflection_prompts), 3)
        self.assertEqual(len(entry.mindful_actions), 3)
        self.assertEqual(len(entry.gratitude_prompts), 3)
        self.assertIsInstance(entry.affirmation, str)

    def test_serialized_entry_contains_iso_date(self):
        entry = generate_entry(date(2025, 2, 25))
        self.assertEqual(entry.to_dict()["date"], "2025-02-25")


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
        self.assertIn("Daily Bread for Tuesday, February 25, 2025", result.stdout)

    def test_json_output_contains_nine_prompts(self):
        result = self.run_cli("--date", "2025-02-25", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["date"], "2025-02-25")
        self.assertEqual(len(payload["reflection_prompts"]), 3)
        self.assertEqual(len(payload["mindful_actions"]), 3)
        self.assertEqual(len(payload["gratitude_prompts"]), 3)

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
