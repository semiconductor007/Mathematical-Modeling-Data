"""Run the complete Question 3 performance-cost workflow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q3.analysis import run_analysis
from src.q3.reporting import generate_mapping, generate_report
from src.q3.visualization import generate_figures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/q3")
    parser.add_argument("--q2-dir", type=Path, default=ROOT / "results/q2")
    parser.add_argument("--docs-dir", type=Path, default=ROOT / "docs")
    args = parser.parse_args()
    try:
        result = run_analysis(ROOT, args.output_dir, args.q2_dir)
        figures = generate_figures(result, args.output_dir)
        report = generate_report(result, args.docs_dir)
        mapping = generate_mapping(args.docs_dir)
    except (AssertionError, FileNotFoundError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    frontier = result["pareto"].loc[result["pareto"]["is_pareto_frontier"], "model"].tolist()
    print(f"Question 3 complete: Pareto frontier={frontier}; generated 8 CSVs, {len(figures)} PNGs, {report.name}, {mapping.name} and final_model_summary.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
