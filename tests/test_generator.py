import json
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from dailybread.generator import DailyBreadEntry, generate_entry
from dailybread.model import SkyObservation, SourceRef
from dailybread.cli import render


ROOT = Path(__file__).resolve().parents[1]
TEST_SOURCE = SourceRef(name="Test ephemeris", reference="fixed fixture")
TEST_SKY = [
    SkyObservation("Sun apparent geocentric ecliptic longitude", "167.500° at 12:00 UTC", TEST_SOURCE),
    SkyObservation("Moon apparent geocentric ecliptic longitude", "42.500° at 12:00 UTC", TEST_SOURCE),
    SkyObservation("Jupiter apparent geocentric ecliptic longitude", "120.000° at 12:00 UTC", TEST_SOURCE),
    SkyObservation("Sun-Jupiter geocentric angular separation", "47.500°", TEST_SOURCE),
    SkyObservation("Moon-Jupiter geocentric angular separation", "77.500°", TEST_SOURCE),
    SkyObservation("Moon illuminated fraction", "61.25% at 12:00 UTC", TEST_SOURCE),
]


class GeneratorTests(unittest.TestCase):
    def generate(self, target=date(2026, 9, 10), ranking_basis="balanced"):
        with patch("dailybread.generator.observations_for", return_value=TEST_SKY):
            return generate_entry(target, ranking_basis=ranking_basis)

    def test_generate_entry_is_deterministic_with_fixed_sky(self):
        self.assertEqual(self.generate(), self.generate())

    def test_entry_structure(self):
        entry = self.generate()
        self.assertIsInstance(entry, DailyBreadEntry)
        self.assertEqual(entry.observations, TEST_SKY)
        self.assertGreaterEqual(len(entry.astrological_factors), 1)
        self.assertIsNotNone(entry.primary_theme)
        self.assertEqual(len(entry.citations), 9)
        self.assertTrue(all(citation.evidence_class == "comparative" for citation in entry.citations))
        self.assertTrue(all(citation.relevance is not None for citation in entry.citations))

    def test_relevance_modes(self):
        for basis in ("astronomy", "astrology", "balanced"):
            entry = self.generate(ranking_basis=basis)
            self.assertEqual(entry.ranking_basis, basis)

    def test_serialized_entry_contains_iso_date(self):
        entry = self.generate()
        self.assertEqual(entry.to_dict()["target_date"], "2026-09-10")

    def test_rendered_output_contains_layers(self):
        text = render(self.generate(), "text")
        self.assertIn("Daily Bread + Nine for Thursday, September 10, 2026", text)
        self.assertIn("Observed Sky", text)
        self.assertIn("Astrological Lens", text)
        self.assertIn("The Plus Nine", text)
        payload = json.loads(render(self.generate(), "json"))
        self.assertEqual(len(payload["citations"]), 9)


class CommandLineValidationTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "dailybread", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_invalid_calendar_date_is_rejected_before_network_use(self):
        result = self.run_cli("--date", "2025-02-30")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Use YYYY-MM-DD", result.stderr)

    def test_noncanonical_date_is_rejected_before_network_use(self):
        result = self.run_cli("--date", "2025-2-5")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Use YYYY-MM-DD", result.stderr)


if __name__ == "__main__":
    unittest.main()
