from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from scripts.model_phase5_scenarios import compute


class Phase5ScenarioTests(unittest.TestCase):
    def test_scenario_weights_and_rankings(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            result = compute(output)
            self.assertEqual(result["scenarios"], 3)
            self.assertEqual(result["ranked_models"], 5)
            with (output / "scenario_weights.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            for scenario in {row["scenario"] for row in rows}:
                total = sum(float(row["combined_weight"]) for row in rows if row["scenario"] == scenario)
                self.assertAlmostEqual(total, 1.0, places=8)


if __name__ == "__main__":
    unittest.main()
