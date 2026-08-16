"""Build three scenario rankings from CRITIC and declared subjective weights."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIORITIES = Path(__file__).with_name("phase5_scenario_priorities.csv")
DEFAULT_OUTPUT = ROOT / "results/phase5"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def topsis(models: list[str], indicators: list[str], normalized: dict[tuple[str, str], float], weights: dict[str, float]) -> dict[str, float]:
    result = {}
    for model in models:
        positive = math.sqrt(sum((weights[key] * normalized[model, key] - weights[key]) ** 2 for key in indicators))
        negative = math.sqrt(sum((weights[key] * normalized[model, key]) ** 2 for key in indicators))
        result[model] = negative / (positive + negative)
    return result


def compute(output_dir: Path, objective_share: float = 0.5) -> dict[str, object]:
    if not 0 <= objective_share <= 1:
        raise ValueError("objective_share must be in [0, 1]")
    normalized_rows = read_rows(ROOT / "results/phase4/normalized_scores.csv")
    critic_rows = read_rows(ROOT / "results/phase4/critic_weights.csv")
    general_rows = read_rows(ROOT / "results/phase4/general_ranking.csv")
    priority_rows = read_rows(PRIORITIES)
    indicators = [row["indicator_key"] for row in critic_rows]
    critic = {row["indicator_key"]: float(row["critic_weight"]) for row in critic_rows}
    names = {row["model_id"]: row["model_name"] for row in normalized_rows}
    general_rank = {row["model_id"]: row["rank"] for row in general_rows}
    ranked_models = [row["model_id"] for row in general_rows if row["ranking_status"] == "ranked_complete_case"]
    normalized = {
        (row["model_id"], row["indicator_key"]): float(row["minmax_score"])
        for row in normalized_rows if row["minmax_score"] != "NA" and row["model_id"] in ranked_models
    }
    scenarios = list(dict.fromkeys(row["scenario"] for row in priority_rows))
    weight_output, ranking_output = [], []
    winners = {}
    for scenario in scenarios:
        subjective = {row["indicator_key"]: float(row["subjective_weight"]) for row in priority_rows if row["scenario"] == scenario}
        if set(subjective) != set(indicators) or abs(sum(subjective.values()) - 1) > 1e-9:
            raise ValueError(f"Scenario {scenario} weights must cover indicators and sum to 1")
        combined = {key: objective_share * critic[key] + (1 - objective_share) * subjective[key] for key in indicators}
        for key in indicators:
            weight_output.append({
                "scenario": scenario,
                "indicator_key": key,
                "critic_weight": f"{critic[key]:.10f}",
                "subjective_weight": f"{subjective[key]:.10f}",
                "objective_share": f"{objective_share:.2f}",
                "combined_weight": f"{combined[key]:.10f}",
            })
        scores = topsis(ranked_models, indicators, normalized, combined)
        ordered = sorted(ranked_models, key=lambda model: (-scores[model], model))
        winners[scenario] = ordered[0]
        for rank, model in enumerate(ordered, start=1):
            ranking_output.append({
                "scenario": scenario,
                "model_id": model,
                "model_name": names[model],
                "scenario_score": f"{scores[model]:.10f}",
                "scenario_rank": str(rank),
                "general_rank": general_rank[model],
                "rank_change_vs_general": str(int(general_rank[model]) - rank),
                "ranking_status": "ranked_complete_case",
            })
        for model in names:
            if model not in ranked_models:
                ranking_output.append({
                    "scenario": scenario, "model_id": model, "model_name": names[model],
                    "scenario_score": "NA", "scenario_rank": "NA", "general_rank": "NA",
                    "rank_change_vs_general": "NA", "ranking_status": "not_ranked_insufficient_coverage",
                })
    write_rows(
        output_dir / "scenario_weights.csv",
        ["scenario", "indicator_key", "critic_weight", "subjective_weight", "objective_share", "combined_weight"],
        weight_output,
    )
    write_rows(
        output_dir / "scenario_rankings.csv",
        ["scenario", "model_id", "model_name", "scenario_score", "scenario_rank", "general_rank", "rank_change_vs_general", "ranking_status"],
        ranking_output,
    )
    return {"scenarios": len(scenarios), "ranked_models": len(ranked_models), "winners": winners}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--objective-share", type=float, default=0.5)
    args = parser.parse_args()
    try:
        result = compute(args.output_dir, args.objective_share)
    except (KeyError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Phase 5 complete: {result['scenarios']} scenarios, winners={result['winners']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
