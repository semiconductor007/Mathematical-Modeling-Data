from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from scripts.analyze_phase3_indicators import analyze, pearson, ranks


class Phase3AnalysisTests(unittest.TestCase):
    def test_rank_ties_and_correlation(self) -> None:
        self.assertEqual(ranks([20, 10, 20]), [2.5, 1.0, 2.5])
        self.assertAlmostEqual(pearson([1, 2, 3], [2, 4, 6]) or 0, 1.0)

    def test_all_frozen_indicators_are_screened(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            result = analyze(output)
            self.assertEqual(result["indicators"], 9)
            self.assertEqual(result["retained"], 9)
            with (output / "indicator_screening.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertTrue(all(row["phase3_decision"] == "retain" for row in rows))
            self.assertTrue(all(float(row["coverage_percent"]) >= 75 for row in rows))


if __name__ == "__main__":
    unittest.main()
