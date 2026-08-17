from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from scripts.model_phase6_cost_benefit import compute


class Phase6CostBenefitTests(unittest.TestCase):
    def test_frontier_and_budget_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            result = compute(output)
            self.assertEqual(result["budget_rows"], 5)
            self.assertGreaterEqual(len(result["frontier"]), 1)
            with (output / "performance_cost.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 6)
            glm = next(row for row in rows if row["model_id"] == "glm-5.2")
            self.assertEqual(glm["general_performance_score"], "NA")


if __name__ == "__main__":
    unittest.main()
