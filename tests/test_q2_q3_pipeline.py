from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.q2.analysis import run_analysis as run_q2
from src.q3.analysis import run_analysis as run_q3


class DownstreamPipelineTests(unittest.TestCase):
    def test_q2_and_q3_invariants(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            temp = Path(folder)
            q2_dir, q3_dir = temp / "q2", temp / "q3"
            q2 = run_q2(root, q2_dir)
            self.assertTrue(q2["scenario_weights"].groupby("scenario")["combined_weight"].sum().sub(1).abs().lt(1e-10).all())
            self.assertEqual(len(q2["sensitivity"]), 540)
            summary_path = temp / "final_model_summary.csv"
            q3 = run_q3(root, q3_dir, q2_dir, summary_path)
            self.assertEqual(set(q3["pareto"].loc[q3["pareto"]["is_pareto_frontier"], "model_id"]), {"kimi-k3", "claude-fable-5"})
            self.assertTrue((q3["budgets"]["cost_usd"] <= q3["budgets"]["budget_limit_usd"]).all())
            self.assertEqual(len(q3["sensitivity"]), 36)
            summary = pd.read_csv(summary_path, encoding="utf-8-sig")
            self.assertEqual(summary["model_id"].nunique(), 6)


if __name__ == "__main__":
    unittest.main()
