"""Run entropy-weight comparison, weight sensitivity, and exploratory regression."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

try:
    from scripts.model_phase5_scenarios import topsis
except ModuleNotFoundError:
    from model_phase5_scenarios import topsis

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results/phase7"
FACTORS = (0.8, 0.9, 1.1, 1.2)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def ordered_ranks(scores: dict[str, float]) -> tuple[list[str], dict[str, int]]:
    order = sorted(scores, key=lambda model: (-scores[model], model))
    return order, {model: rank for rank, model in enumerate(order, start=1)}


def kendall_tau(rank_a: dict[str, int], rank_b: dict[str, int]) -> float:
    models = sorted(rank_a)
    concordant = discordant = 0
    for i, left in enumerate(models):
        for right in models[i + 1:]:
            product = (rank_a[left] - rank_a[right]) * (rank_b[left] - rank_b[right])
            concordant += product > 0
            discordant += product < 0
    return (concordant - discordant) / (concordant + discordant)


def entropy_weights(models: list[str], indicators: list[str], normalized: dict[tuple[str, str], float]) -> dict[str, float]:
    diversification = {}
    scale = 1 / math.log(len(models))
    for indicator in indicators:
        values = [normalized[model, indicator] for model in models]
        total = sum(values)
        probabilities = [value / total for value in values] if total else [1 / len(models)] * len(models)
        entropy = -scale * sum(probability * math.log(probability) for probability in probabilities if probability > 0)
        diversification[indicator] = 1 - entropy
    total = sum(diversification.values())
    return {indicator: diversification[indicator] / total for indicator in indicators}


def linear_regression(x: list[float], y: list[float]) -> tuple[float, float, float]:
    x_mean, y_mean = sum(x) / len(x), sum(y) / len(y)
    denominator = sum((value - x_mean) ** 2 for value in x)
    slope = sum((a - x_mean) * (b - y_mean) for a, b in zip(x, y)) / denominator
    intercept = y_mean - slope * x_mean
    fitted = [intercept + slope * value for value in x]
    residual = sum((actual - predicted) ** 2 for actual, predicted in zip(y, fitted))
    total = sum((actual - y_mean) ** 2 for actual in y)
    return intercept, slope, 1 - residual / total if total else 0.0


def analyze(output_dir: Path) -> dict[str, object]:
    normalized_rows = read_rows(ROOT / "results/phase4/normalized_scores.csv")
    critic_rows = read_rows(ROOT / "results/phase4/critic_weights.csv")
    ranking_rows = read_rows(ROOT / "results/phase4/general_ranking.csv")
    cost_rows = read_rows(ROOT / "results/phase6/performance_cost.csv")
    indicators = [row["indicator_key"] for row in critic_rows]
    critic = {row["indicator_key"]: float(row["critic_weight"]) for row in critic_rows}
    models = [row["model_id"] for row in ranking_rows if row["ranking_status"] == "ranked_complete_case"]
    names = {row["model_id"]: row["model_name"] for row in ranking_rows}
    normalized = {
        (row["model_id"], row["indicator_key"]): float(row["minmax_score"])
        for row in normalized_rows if row["model_id"] in models and row["minmax_score"] != "NA"
    }
    entropy = entropy_weights(models, indicators, normalized)
    critic_scores = topsis(models, indicators, normalized, critic)
    entropy_scores = topsis(models, indicators, normalized, entropy)
    critic_order, critic_rank = ordered_ranks(critic_scores)
    entropy_order, entropy_rank = ordered_ranks(entropy_scores)
    method_rows = []
    for model in critic_order:
        method_rows.append({
            "model_id": model, "model_name": names[model],
            "critic_score": f"{critic_scores[model]:.10f}", "critic_rank": str(critic_rank[model]),
            "entropy_score": f"{entropy_scores[model]:.10f}", "entropy_rank": str(entropy_rank[model]),
            "rank_difference": str(entropy_rank[model] - critic_rank[model]),
        })
    write_rows(
        output_dir / "method_comparison.csv",
        ["model_id", "model_name", "critic_score", "critic_rank", "entropy_score", "entropy_rank", "rank_difference"],
        method_rows,
    )
    weight_rows = [
        {"indicator_key": key, "critic_weight": f"{critic[key]:.10f}", "entropy_weight": f"{entropy[key]:.10f}", "difference": f"{entropy[key] - critic[key]:.10f}"}
        for key in indicators
    ]
    write_rows(output_dir / "weight_method_comparison.csv", ["indicator_key", "critic_weight", "entropy_weight", "difference"], weight_rows)

    perturb_rows = []
    rank_history: dict[str, list[int]] = defaultdict(list)
    top_counts: dict[str, int] = defaultdict(int)
    tau_rows = []
    scenario_count = 0
    for indicator in indicators:
        for factor in FACTORS:
            adjusted = dict(critic)
            adjusted[indicator] *= factor
            total = sum(adjusted.values())
            adjusted = {key: value / total for key, value in adjusted.items()}
            scores = topsis(models, indicators, normalized, adjusted)
            order, ranks = ordered_ranks(scores)
            scenario = f"{indicator}_x{factor:.1f}"
            scenario_count += 1
            top_counts[order[0]] += 1
            tau_rows.append({"scenario": scenario, "kendall_tau_vs_baseline": f"{kendall_tau(critic_rank, ranks):.10f}", "winner": order[0]})
            for model in order:
                rank_history[model].append(ranks[model])
                perturb_rows.append({
                    "scenario": scenario, "perturbed_indicator": indicator, "factor": f"{factor:.1f}",
                    "model_id": model, "score": f"{scores[model]:.10f}", "rank": str(ranks[model]),
                    "rank_change_vs_baseline": str(critic_rank[model] - ranks[model]),
                })
    write_rows(
        output_dir / "weight_perturbation_rankings.csv",
        ["scenario", "perturbed_indicator", "factor", "model_id", "score", "rank", "rank_change_vs_baseline"],
        perturb_rows,
    )
    write_rows(output_dir / "rank_correlation.csv", ["scenario", "kendall_tau_vs_baseline", "winner"], tau_rows)
    stability_rows = []
    for model in critic_order:
        history = rank_history[model]
        stability_rows.append({
            "model_id": model, "model_name": names[model], "baseline_rank": str(critic_rank[model]),
            "minimum_rank": str(min(history)), "maximum_rank": str(max(history)),
            "mean_rank": f"{sum(history) / len(history):.4f}",
            "top1_frequency": f"{top_counts[model] / scenario_count:.4f}",
        })
    write_rows(
        output_dir / "rank_stability.csv",
        ["model_id", "model_name", "baseline_rank", "minimum_rank", "maximum_rank", "mean_rank", "top1_frequency"],
        stability_rows,
    )

    included_cost = [row for row in cost_rows if row["analysis_status"] == "included"]
    x = [math.log(float(row["standardized_api_cost_usd"])) for row in included_cost]
    y = [float(row["general_performance_score"]) for row in included_cost]
    intercept, slope, r_squared = linear_regression(x, y)
    regression_rows = [{
        "model": "performance = intercept + slope * ln(cost)",
        "n": str(len(x)), "intercept": f"{intercept:.10f}", "slope_log_cost": f"{slope:.10f}",
        "r_squared": f"{r_squared:.10f}", "interpretation": "exploratory only; n=5 is too small for causal inference",
    }]
    write_rows(output_dir / "cost_performance_regression.csv", list(regression_rows[0]), regression_rows)
    return {
        "entropy_winner": entropy_order[0],
        "scenarios": scenario_count,
        "minimum_tau": min(float(row["kendall_tau_vs_baseline"]) for row in tau_rows),
        "regression_r_squared": r_squared,
    }


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
        f"Phase 7 complete: {result['scenarios']} perturbations, entropy winner={result['entropy_winner']}, "
        f"minimum Kendall tau={result['minimum_tau']:.3f}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
