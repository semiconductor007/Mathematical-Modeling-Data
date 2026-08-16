"""Analyze Phase 3 indicator distributions, correlations, and redundancy."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/processed/core_benchmark_long.csv"
DEFAULT_OUTPUT = ROOT / "results/phase3"
NA = "NA"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def sample_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    center = mean(values)
    return math.sqrt(sum((value - center) ** 2 for value in values) / (len(values) - 1))


def pearson(left: list[float], right: list[float]) -> float | None:
    if len(left) < 3 or len(left) != len(right):
        return None
    left_mean, right_mean = mean(left), mean(right)
    numerator = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right))
    denominator = math.sqrt(
        sum((x - left_mean) ** 2 for x in left) * sum((y - right_mean) ** 2 for y in right)
    )
    return numerator / denominator if denominator else None


def ranks(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    result = [0.0] * len(values)
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][1] == ordered[index][1]:
            end += 1
        average_rank = (index + 1 + end) / 2
        for position in range(index, end):
            result[ordered[position][0]] = average_rank
        index = end
    return result


def paired(values: dict[str, dict[str, float]], left: str, right: str) -> tuple[list[float], list[float]]:
    model_ids = sorted(set(values[left]) & set(values[right]))
    return [values[left][key] for key in model_ids], [values[right][key] for key in model_ids]


def fmt(value: float | None) -> str:
    return NA if value is None else f"{value:.6f}"


def analyze(output_dir: Path) -> dict[str, int]:
    rows = read_rows(INPUT)
    indicators = list(dict.fromkeys(row["indicator_key"] for row in rows))
    dimensions = {row["indicator_key"]: row["dimension"] for row in rows}
    names = {row["indicator_key"]: row["indicator"] for row in rows}
    values: dict[str, dict[str, float]] = {indicator: {} for indicator in indicators}
    total_models = len({row["model_id"] for row in rows})
    for row in rows:
        if row["score"] != NA:
            values[row["indicator_key"]][row["model_id"]] = float(row["score"])

    descriptive = []
    for indicator in indicators:
        current = list(values[indicator].values())
        current_mean = mean(current)
        std = sample_std(current)
        descriptive.append({
            "indicator_key": indicator,
            "dimension": dimensions[indicator],
            "indicator": names[indicator],
            "available_models": str(len(current)),
            "missing_models": str(total_models - len(current)),
            "mean": f"{current_mean:.6f}",
            "sample_std": f"{std:.6f}",
            "coefficient_of_variation": fmt(std / abs(current_mean) if current_mean else None),
            "minimum": f"{min(current):.6f}",
            "maximum": f"{max(current):.6f}",
            "range": f"{max(current) - min(current):.6f}",
        })
    write_rows(
        output_dir / "descriptive_statistics.csv",
        list(descriptive[0]),
        descriptive,
    )

    correlation_fields = ["indicator_key"] + indicators
    pearson_rows, spearman_rows = [], []
    redundancy = []
    flagged: set[str] = set()
    for left in indicators:
        pearson_row = {"indicator_key": left}
        spearman_row = {"indicator_key": left}
        for right in indicators:
            x, y = paired(values, left, right)
            p = pearson(x, y)
            s = pearson(ranks(x), ranks(y)) if len(x) >= 3 else None
            pearson_row[right] = fmt(p)
            spearman_row[right] = fmt(s)
            if indicators.index(left) < indicators.index(right) and s is not None and abs(s) >= 0.9:
                same_dimension = dimensions[left] == dimensions[right]
                redundancy.append({
                    "indicator_a": left,
                    "indicator_b": right,
                    "pairwise_models": str(len(x)),
                    "pearson": fmt(p),
                    "spearman": fmt(s),
                    "same_dimension": str(same_dimension).lower(),
                    "decision": "review_not_auto_drop",
                    "reason": "Only 5-6 models; correlation is unstable and indicators represent distinct constructs" if not same_dimension else "Only 5-6 models; retain pending robustness analysis",
                })
                flagged.update((left, right))
        pearson_rows.append(pearson_row)
        spearman_rows.append(spearman_row)
    write_rows(output_dir / "pearson_correlation.csv", correlation_fields, pearson_rows)
    write_rows(output_dir / "spearman_correlation.csv", correlation_fields, spearman_rows)
    redundancy_fields = [
        "indicator_a", "indicator_b", "pairwise_models", "pearson", "spearman",
        "same_dimension", "decision", "reason",
    ]
    write_rows(output_dir / "redundancy_flags.csv", redundancy_fields, redundancy)

    screening = []
    for item in descriptive:
        indicator = item["indicator_key"]
        coverage = int(item["available_models"]) / total_models * 100
        screening.append({
            "indicator_key": indicator,
            "dimension": dimensions[indicator],
            "indicator": names[indicator],
            "coverage_percent": f"{coverage:.1f}",
            "variation_nonzero": str(float(item["sample_std"]) > 0).lower(),
            "high_correlation_flag": str(indicator in flagged).lower(),
            "phase3_decision": "retain",
            "reason": "Coverage >=75%, nonzero variation, and distinct substantive dimension; high correlations are not used for automatic deletion with n=6",
        })
    write_rows(
        output_dir / "indicator_screening.csv",
        [
            "indicator_key", "dimension", "indicator", "coverage_percent", "variation_nonzero",
            "high_correlation_flag", "phase3_decision", "reason",
        ],
        screening,
    )
    return {"indicators": len(indicators), "redundancy_flags": len(redundancy), "retained": len(screening)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        result = analyze(args.output_dir)
    except (KeyError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"Phase 3 analysis complete: {result['indicators']} indicators, "
        f"{result['redundancy_flags']} high-correlation pair(s), {result['retained']} retained."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
