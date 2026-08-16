from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from scripts.analyze_phase7_robustness import analyze, kendall_tau


class Phase7RobustnessTests(unittest.TestCase):
    def test_kendall_tau(self) -> None:
        baseline = {"a": 1, "b": 2, "c": 3}
        self.assertEqual(kendall_tau(baseline, baseline), 1.0)
        self.assertEqual(kendall_tau(baseline, {"a": 3, "b": 2, "c": 1}), -1.0)

    def test_sensitivity_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            result = analyze(output)
            self.assertEqual(result["scenarios"], 36)
            with (output / "rank_stability.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 5)
            self.assertTrue(all(int(row["minimum_rank"]) <= int(row["maximum_rank"]) for row in rows))


if __name__ == "__main__":
    unittest.main()
