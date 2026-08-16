"""Report per-benchmark model coverage without imputing missing values."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NA_VALUES = {"", "na", "n/a", "null", "none"}


def is_present(value: str | None) -> bool:
    return value is not None and value.strip().lower() not in NA_VALUES


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=ROOT / "data/model_candidates.csv")
    parser.add_argument("--scores", type=Path, default=ROOT / "data/raw/benchmark_scores.csv")
    args = parser.parse_args()

    candidates = read_rows(args.candidates)
    scores = read_rows(args.scores)
    model_ids = {row.get("model_id", "").strip() for row in candidates if is_present(row.get("model_id"))}
    by_benchmark: dict[str, set[str]] = {}
    for row in scores:
        benchmark = row.get("benchmark", "").strip()
        model_id = row.get("model_id", "").strip()
        if is_present(benchmark) and model_id in model_ids and is_present(row.get("score")):
            by_benchmark.setdefault(benchmark, set()).add(model_id)

    total = len(model_ids)
    if not by_benchmark:
        print(f"No benchmark observations found. Candidate models: {total}.")
        return 0

    output = []
    for benchmark in sorted(by_benchmark):
        present = by_benchmark[benchmark]
        coverage = len(present) / total if total else 0.0
        missing = ", ".join(sorted(model_ids - present)) or "-"
        output.append((benchmark, len(present), total, f"{coverage:.1%}", missing))

    headers = ("Benchmark", "Models", "Total", "Coverage", "Missing model_ids")
    widths = [max(len(str(row[i])) for row in [headers, *output]) for i in range(len(headers))]
    print(" | ".join(str(headers[i]).ljust(widths[i]) for i in range(len(headers))))
    print("-+-".join("-" * width for width in widths))
    for row in output:
        print(" | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
