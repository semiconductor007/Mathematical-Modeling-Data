"""Report raw and strictly comparable benchmark coverage without imputation."""

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
    parser.add_argument("--output", type=Path, help="Optional CSV path for the coverage report")
    args = parser.parse_args()

    candidates = read_rows(args.candidates)
    scores = read_rows(args.scores)
    model_ids = {row.get("model_id", "").strip() for row in candidates if is_present(row.get("model_id"))}
    by_benchmark: dict[str, set[str]] = {}
    compatible_cohorts: dict[str, dict[tuple[str, str, str], set[str]]] = {}
    for row in scores:
        benchmark = row.get("benchmark", "").strip()
        model_id = row.get("model_id", "").strip()
        if is_present(benchmark) and model_id in model_ids and is_present(row.get("score")):
            by_benchmark.setdefault(benchmark, set()).add(model_id)
            if row.get("compatible", "").strip().lower() == "true":
                cohort = (
                    row.get("benchmark_version", "").strip(),
                    row.get("test_setting", "").strip(),
                    row.get("source_name", "").strip(),
                )
                compatible_cohorts.setdefault(benchmark, {}).setdefault(cohort, set()).add(model_id)

    total = len(model_ids)
    if not by_benchmark:
        print(f"No benchmark observations found. Candidate models: {total}.")
        return 0

    output = []
    for benchmark in sorted(by_benchmark):
        raw_present = by_benchmark[benchmark]
        cohorts = compatible_cohorts.get(benchmark, {})
        best_key, best_present = max(
            cohorts.items(), key=lambda item: (len(item[1]), item[0]), default=(("-", "-", "-"), set())
        )
        raw_coverage = len(raw_present) / total if total else 0.0
        comparable_coverage = len(best_present) / total if total else 0.0
        missing = ", ".join(sorted(model_ids - best_present)) or "-"
        cohort_label = f"{best_key[0]} | {best_key[1]}" if best_present else "none"
        output.append((
            benchmark,
            len(raw_present),
            len(best_present),
            total,
            f"{raw_coverage:.1%}",
            f"{comparable_coverage:.1%}",
            missing,
            cohort_label,
        ))

    headers = (
        "Benchmark", "Raw", "Comparable", "Total", "Raw coverage",
        "Comparable coverage", "Missing from best cohort", "Best comparable cohort",
    )
    widths = [max(len(str(row[i])) for row in [headers, *output]) for i in range(len(headers))]
    print(" | ".join(str(headers[i]).ljust(widths[i]) for i in range(len(headers))))
    print("-+-".join("-" * width for width in widths))
    for row in output:
        print(" | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(output)
        print(f"Coverage report written to {args.output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
