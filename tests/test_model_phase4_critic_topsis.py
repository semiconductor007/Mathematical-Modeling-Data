from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from scripts.model_phase4_critic_topsis import compute, minmax


class Phase4ModelTests(unittest.TestCase):
    def test_minmax_directions(self) -> None:
        self.assertEqual(minmax({"a": 1.0, "b": 3.0}, True), {"a": 0.0, "b": 1.0})
        self.assertEqual(minmax({"a": 1.0, "b": 3.0}, False), {"a": 1.0, "b": 0.0})

    def test_weights_sum_and_missing_model_is_not_ranked(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            result = compute(output)
            self.assertAlmostEqual(sum(result["weights"].values()), 1.0)
            self.assertEqual(result["ranked_models"], 5)
            with (output / "general_ranking.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            glm = next(row for row in rows if row["model_id"] == "glm-5.2")
            self.assertEqual(glm["rank"], "NA")
            self.assertEqual(glm["ranking_status"], "not_ranked_insufficient_coverage")


if __name__ == "__main__":
    unittest.main()
