"""Run the complete reproducible Question 1 modeling workflow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q1.analysis import run_analysis
from src.q1.reporting import generate_documents
from src.q1.visualization import generate_figures
from scripts.validate_q1 import CSV_FILES, validate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/q1")
    parser.add_argument("--docs-dir", type=Path, default=ROOT / "docs")
    args = parser.parse_args()
    try:
        result = run_analysis(ROOT, args.output_dir)
        figures = generate_figures(result, args.output_dir)
        documents = generate_documents(result, args.docs_dir)
        issues = validate(args.output_dir, args.docs_dir)
        if issues:
            raise AssertionError("; ".join(issues))
    except (AssertionError, FileNotFoundError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    ranked = result["ranking"]
    winner = ranked.loc[ranked["rank"] == 1, "model"].iloc[0]
    kimi_rank = int(ranked.loc[ranked["model_id"] == "kimi-k3", "rank"].iloc[0])
    print(
        f"Question 1 complete: {len(result['models'])} models, {len(result['metrics'])} indicators, "
        f"winner={winner}, Kimi rank={kimi_rank}; generated {len(CSV_FILES)} CSVs, "
        f"{len(figures)} PNGs and {len(documents)} documents."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
