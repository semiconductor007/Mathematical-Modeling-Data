"""Generate the GLM-5.2 supplemental Q1 analysis required by model(1).md."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.q1.glm_supplement import generate_figure, run_analysis


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/phase4b")
    args = parser.parse_args()
    try:
        result = run_analysis(ROOT, args.output_dir)
        figure = generate_figure(result, args.output_dir)
    except (AssertionError, FileNotFoundError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"GLM supplement complete: {len(result['comparison'])} directly comparable metrics; figure={figure.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
