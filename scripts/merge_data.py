"""Safely merge raw tables by model_id while preserving NA values.

The current scaffold writes one row per candidate and stores all matching raw
records as JSON arrays. It deliberately performs no imputation, aggregation,
deduplication, or score selection.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def grouped(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        result[row.get("model_id", "")].append(row)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "data/merged/model_dataset.csv")
    parser.add_argument("--force", action="store_true", help="Replace an existing output file")
    args = parser.parse_args()
    if args.output.exists() and not args.force:
        print(f"Refusing to overwrite existing file: {args.output}. Use --force after review.")
        return 2

    candidates = read_rows(ROOT / "data/model_candidates.csv")
    benchmarks = grouped(read_rows(ROOT / "data/raw/benchmark_scores.csv"))
    metadata = grouped(read_rows(ROOT / "data/raw/model_metadata.csv"))
    efficiency = grouped(read_rows(ROOT / "data/raw/cost_efficiency.csv"))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["model_id", "provider", "model_name", "exact_version", "candidate_status", "benchmark_records", "metadata_records", "efficiency_records"]
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for candidate in candidates:
            model_id = candidate.get("model_id", "")
            writer.writerow({
                "model_id": model_id,
                "provider": candidate.get("provider", "NA") or "NA",
                "model_name": candidate.get("model_name", "NA") or "NA",
                "exact_version": candidate.get("exact_version", "NA") or "NA",
                "candidate_status": candidate.get("candidate_status", "NA") or "NA",
                "benchmark_records": json.dumps(benchmarks.get(model_id, []), ensure_ascii=False),
                "metadata_records": json.dumps(metadata.get(model_id, []), ensure_ascii=False),
                "efficiency_records": json.dumps(efficiency.get(model_id, []), ensure_ascii=False),
            })
    print(f"Wrote {len(candidates)} candidate row(s) to {args.output}; no values were imputed or discarded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
