from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.q1.analysis import run_analysis


class Question1PipelineTests(unittest.TestCase):
    def test_q1_outputs_and_invariants(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            result = run_analysis(root, Path(folder))
            weights = result["weights"]
            ranking = result["ranking"]
            self.assertAlmostEqual(float(weights["weight"].sum()), 1.0, places=10)
            ranked = ranking.loc[ranking["ranking_status"] == "ranked_complete_case"]
            self.assertTrue(ranked["topsis_score"].between(0, 1).all())
            self.assertEqual(ranking["model_id"].nunique(), 6)
            self.assertEqual(len(result["metrics"]), 9)
            self.assertEqual(int(ranked.loc[ranked["model_id"] == "kimi-k3", "rank"].iloc[0]), 2)
            self.assertTrue((Path(folder) / "rank_stability.csv").exists())
            reread = pd.read_csv(Path(folder) / "normalized_data.csv", encoding="utf-8-sig")
            self.assertEqual(len(reread), 6)


if __name__ == "__main__":
    unittest.main()
