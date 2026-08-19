"""Rebuild and validate all committed datasets, models, results, and figures."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    ["scripts/process_phase2_data.py"],
    ["scripts/merge_data.py", "--final-only", "--force"],
    ["scripts/validate_data.py"],
    ["scripts/check_coverage.py", "--output", "results/benchmark_coverage.csv"],
    ["scripts/analyze_phase3_indicators.py"],
    ["scripts/model_phase4_critic_topsis.py"],
    ["scripts/run_glm_supplement.py"],
    ["scripts/model_phase5_scenarios.py"],
    ["scripts/model_phase6_cost_benefit.py"],
    ["scripts/analyze_phase7_robustness.py"],
    ["scripts/generate_figures.py"],
    ["scripts/validate_modeling.py"],
]


def main() -> int:
    for arguments in COMMANDS:
        print(f"\n==> {sys.executable} {' '.join(arguments)}", flush=True)
        completed = subprocess.run([sys.executable, *arguments], cwd=ROOT, check=False)
        if completed.returncode:
            print(f"Pipeline stopped with exit code {completed.returncode}: {' '.join(arguments)}")
            return completed.returncode
    print("\nPipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
