"""Run the complete Question 2 scenario-evaluation workflow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q2.analysis import run_analysis
from src.q2.reporting import generate_report
from src.q2.visualization import generate_figures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/q2")
    parser.add_argument("--docs-dir", type=Path, default=ROOT / "docs")
    args = parser.parse_args()
    try:
        result = run_analysis(ROOT, args.output_dir)
        figures = generate_figures(result, args.output_dir)
        report = generate_report(result, args.docs_dir)
    except (AssertionError, FileNotFoundError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    rankings = result["scenario_rankings"]
    winners = rankings.loc[rankings["rank"] == 1].set_index("scenario")["model"].to_dict()
    print(f"Question 2 complete: winners={winners}; generated 9 CSVs, {len(figures)} PNGs and {report.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
