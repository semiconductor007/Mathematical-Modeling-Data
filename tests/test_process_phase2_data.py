from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.process_phase2_data import ROOT, build


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Phase2ProcessorTests(unittest.TestCase):
    def test_builds_frozen_matrix_without_touching_raw(self) -> None:
        raw_paths = sorted((ROOT / "data/raw").glob("*.csv"))
        before = {path: digest(path) for path in raw_paths}
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            counts = build(output)
            self.assertEqual(counts, {"models": 6, "indicators": 9, "long_rows": 54})
            with (output / "core_benchmark_matrix.csv").open(encoding="utf-8", newline="") as handle:
                matrix = list(csv.DictReader(handle))
            self.assertEqual(len(matrix), 6)
            self.assertEqual({row["model_id"] for row in matrix}, {
                "kimi-k3", "gpt-5.6-sol", "claude-fable-5", "claude-opus-4.8", "gpt-5.5", "glm-5.2"
            })
            glm = next(row for row in matrix if row["model_id"] == "glm-5.2")
            self.assertEqual(glm["hle_full_no_tools"], "NA")
            with (output / "core_benchmark_long.csv").open(encoding="utf-8", newline="") as handle:
                long_rows = list(csv.DictReader(handle))
            glm_missing = [row for row in long_rows if row["model_id"] == "glm-5.2" and row["score"] == "NA"]
            self.assertEqual(len(glm_missing), 5)
            self.assertEqual(
                sum(row["missing_reason"] == "not applicable: frozen model is text-only" for row in glm_missing),
                4,
            )
            self.assertEqual(
                sum(row["missing_reason"] == "not reported in frozen cohort" for row in glm_missing),
                1,
            )
            with (output / "indicator_quality.csv").open(encoding="utf-8", newline="") as handle:
                quality = list(csv.DictReader(handle))
            self.assertEqual(len(quality), 9)
            self.assertTrue(all(row["cohort_status"] == "pass" for row in quality))
        self.assertEqual(before, {path: digest(path) for path in raw_paths})

    def test_incompatible_efficiency_is_excluded_only_from_comparable_fields(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            build(output)
            with (output / "model_attributes.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            fable = next(row for row in rows if row["model_id"] == "claude-fable-5")
            self.assertNotEqual(fable["observed_ttft_seconds"], "NA")
            self.assertEqual(fable["comparable_ttft_seconds"], "NA")
            self.assertEqual(fable["efficiency_compatible"], "false")


if __name__ == "__main__":
    unittest.main()
