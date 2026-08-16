"""Compute CRITIC weights and a no-imputation TOPSIS general ranking."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

try:
    from scripts.analyze_phase3_indicators import pearson
except ModuleNotFoundError:  # Direct execution adds scripts/, not repository root, to sys.path.
    from analyze_phase3_indicators import pearson

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/processed/core_benchmark_long.csv"
DEFAULT_OUTPUT = ROOT / "results/phase4"
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


def minmax(values: dict[str, float], higher_is_better: bool) -> dict[str, float]:
    low, high = min(values.values()), max(values.values())
    if high == low:
        return {key: 0.5 for key in values}
    if higher_is_better:
        return {key: (value - low) / (high - low) for key, value in values.items()}
    return {key: (high - value) / (high - low) for key, value in values.items()}


def population_std(values: list[float]) -> float:
    center = sum(values) / len(values)
    return math.sqrt(sum((value - center) ** 2 for value in values) / len(values))


def compute(output_dir: Path) -> dict[str, object]:
    rows = read_rows(INPUT)
    indicators = list(dict.fromkeys(row["indicator_key"] for row in rows))
    models = list(dict.fromkeys(row["model_id"] for row in rows))
    names = {row["model_id"]: row["model_name"] for row in rows}
    dimensions = {row["indicator_key"]: row["dimension"] for row in rows}
    indicator_names = {row["indicator_key"]: row["indicator"] for row in rows}
    raw: dict[str, dict[str, float]] = {indicator: {} for indicator in indicators}
    for row in rows:
        if row["score"] != NA:
            raw[row["indicator_key"]][row["model_id"]] = float(row["score"])
    normalized = {
        indicator: minmax(raw[indicator], next(row["higher_is_better"] == "true" for row in rows if row["indicator_key"] == indicator))
        for indicator in indicators
    }

    normalization_rows = []
    for model_id in models:
        for indicator in indicators:
            normalization_rows.append({
                "model_id": model_id,
                "model_name": names[model_id],
                "indicator_key": indicator,
                "raw_score": f"{raw[indicator][model_id]:.10g}" if model_id in raw[indicator] else NA,
                "minmax_score": f"{normalized[indicator][model_id]:.10f}" if model_id in normalized[indicator] else NA,
                "normalization": "benefit_minmax_available_observations",
            })
    write_rows(
        output_dir / "normalized_scores.csv",
        ["model_id", "model_name", "indicator_key", "raw_score", "minmax_score", "normalization"],
        normalization_rows,
    )

    information: dict[str, float] = {}
    weight_rows = []
    for left in indicators:
        correlations = []
        for right in indicators:
            if left == right:
                continue
            common = sorted(set(normalized[left]) & set(normalized[right]))
            correlation = pearson(
                [normalized[left][model] for model in common],
                [normalized[right][model] for model in common],
            )
            if correlation is None:
                raise ValueError(f"Cannot compute correlation for {left}/{right}")
            correlations.append(correlation)
        contrast = population_std(list(normalized[left].values()))
        conflict = sum(1 - value for value in correlations)
        information[left] = contrast * conflict
        weight_rows.append({
            "indicator_key": left,
            "dimension": dimensions[left],
            "indicator": indicator_names[left],
            "available_models": str(len(normalized[left])),
            "contrast_std": f"{contrast:.10f}",
            "conflict_sum": f"{conflict:.10f}",
            "information_content": f"{information[left]:.10f}",
            "critic_weight": "",
        })
    total_information = sum(information.values())
    if total_information <= 0:
        raise ValueError("CRITIC information total must be positive")
    weights = {key: value / total_information for key, value in information.items()}
    for row in weight_rows:
        row["critic_weight"] = f"{weights[row['indicator_key']]:.10f}"
    write_rows(output_dir / "critic_weights.csv", list(weight_rows[0]), weight_rows)

    complete = [model for model in models if all(model in normalized[indicator] for indicator in indicators)]
    if len(complete) < 2:
        raise ValueError("TOPSIS requires at least two complete models")
    ranked = []
    for model_id in complete:
        positive = math.sqrt(sum((weights[indicator] * normalized[indicator][model_id] - weights[indicator]) ** 2 for indicator in indicators))
        negative = math.sqrt(sum((weights[indicator] * normalized[indicator][model_id]) ** 2 for indicator in indicators))
        closeness = negative / (positive + negative)
        ranked.append((model_id, closeness, positive, negative))
    ranked.sort(key=lambda item: (-item[1], item[0]))
    rank_lookup = {model_id: index for index, (model_id, *_rest) in enumerate(ranked, start=1)}
    score_lookup = {model_id: values for model_id, *values in ranked}
    ranking_rows = []
    for model_id in models:
        available = sum(model_id in normalized[indicator] for indicator in indicators)
        if model_id in score_lookup:
            closeness, positive, negative = score_lookup[model_id]
            ranking_rows.append({
                "model_id": model_id, "model_name": names[model_id], "available_indicators": str(available),
                "total_indicators": str(len(indicators)), "coverage_percent": f"{available / len(indicators) * 100:.1f}",
                "distance_positive": f"{positive:.10f}", "distance_negative": f"{negative:.10f}",
                "topsis_score": f"{closeness:.10f}", "rank": str(rank_lookup[model_id]), "ranking_status": "ranked_complete_case",
            })
        else:
            ranking_rows.append({
                "model_id": model_id, "model_name": names[model_id], "available_indicators": str(available),
                "total_indicators": str(len(indicators)), "coverage_percent": f"{available / len(indicators) * 100:.1f}",
                "distance_positive": NA, "distance_negative": NA, "topsis_score": NA, "rank": NA,
                "ranking_status": "not_ranked_insufficient_coverage",
            })
    ranking_rows.sort(key=lambda row: (row["rank"] == NA, int(row["rank"]) if row["rank"] != NA else 999))
    write_rows(
        output_dir / "general_ranking.csv",
        [
            "model_id", "model_name", "available_indicators", "total_indicators", "coverage_percent",
            "distance_positive", "distance_negative", "topsis_score", "rank", "ranking_status",
        ],
        ranking_rows,
    )

    kimi_rows = []
    kimi_id = "kimi-k3"
    for indicator in indicators:
        ordered = sorted(normalized[indicator], key=lambda model: (-normalized[indicator][model], model))
        leader = ordered[0]
        kimi_rank = ordered.index(kimi_id) + 1
        kimi_rows.append({
            "indicator_key": indicator,
            "dimension": dimensions[indicator],
            "indicator": indicator_names[indicator],
            "kimi_normalized_score": f"{normalized[indicator][kimi_id]:.10f}",
            "kimi_rank": str(kimi_rank),
            "models_compared": str(len(ordered)),
            "leader_model_id": leader,
            "gap_to_leader": f"{normalized[indicator][leader] - normalized[indicator][kimi_id]:.10f}",
            "assessment": "strength" if kimi_rank <= 2 else "weakness" if kimi_rank >= len(ordered) - 1 else "middle",
        })
    write_rows(
        output_dir / "kimi_strengths_weaknesses.csv",
        [
            "indicator_key", "dimension", "indicator", "kimi_normalized_score", "kimi_rank",
            "models_compared", "leader_model_id", "gap_to_leader", "assessment",
        ],
        kimi_rows,
    )
    return {
        "weights": weights,
        "ranked_models": len(complete),
        "unranked_models": len(models) - len(complete),
        "winner": ranked[0][0],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        result = compute(args.output_dir)
    except (KeyError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"Phase 4 complete: {result['ranked_models']} complete models ranked, "
        f"{result['unranked_models']} unranked without imputation; winner={result['winner']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
