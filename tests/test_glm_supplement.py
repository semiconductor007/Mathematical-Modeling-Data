from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.q1.glm_supplement import run_analysis


class GlmSupplementTests(unittest.TestCase):
    def test_partial_comparison_and_official_hle_separation(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            result = run_analysis(root, Path(folder))
            self.assertEqual(len(result["comparison"]), 4)
            self.assertEqual(result["comparison"]["models_compared"].tolist(), [6, 6, 6, 6])
            self.assertFalse(bool(result["hle"].iloc[0]["directly_comparable_to_frozen_cohort"]))
            self.assertEqual(float(result["hle"].iloc[0]["official_score"]), 40.5)


if __name__ == "__main__":
    unittest.main()
