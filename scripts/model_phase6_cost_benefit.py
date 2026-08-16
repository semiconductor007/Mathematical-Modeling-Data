"""Evaluate performance, API cost, engineering efficiency, and budget choices."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

try:
    from scripts.model_phase4_critic_topsis import minmax
except ModuleNotFoundError:
    from model_phase4_critic_topsis import minmax

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results/phase6"
NA = "NA"
INPUT_MILLION_TOKENS = 1.0
OUTPUT_MILLION_TOKENS = 0.2
BUDGETS_USD = (6.0, 10.0, 12.0, 16.0)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def compute(output_dir: Path) -> dict[str, object]:
    attributes = read_rows(ROOT / "data/processed/model_attributes.csv")
    ranking = read_rows(ROOT / "results/phase4/general_ranking.csv")
    rank_by_id = {row["model_id"]: row for row in ranking}
    model_names = {row["model_id"]: row["model_name"] for row in attributes}
    costs = {
        row["model_id"]: float(row["input_price_usd_per_million"]) * INPUT_MILLION_TOKENS
        + float(row["output_price_usd_per_million"]) * OUTPUT_MILLION_TOKENS
        for row in attributes
        if row["input_price_usd_per_million"] != NA and row["output_price_usd_per_million"] != NA
    }
    performance = {
        row["model_id"]: float(row["topsis_score"])
        for row in ranking if row["topsis_score"] != NA
    }
    ranked_ids = list(performance)
    frontier = set()
    for model in ranked_ids:
        dominated = any(
            other != model
            and costs[other] <= costs[model]
            and performance[other] >= performance[model]
            and (costs[other] < costs[model] or performance[other] > performance[model])
            for other in ranked_ids
        )
        if not dominated:
            frontier.add(model)
    value_rows = []
    for row in attributes:
        model = row["model_id"]
        score = performance.get(model)
        value_rows.append({
            "model_id": model,
            "model_name": row["model_name"],
            "workload_input_million_tokens": f"{INPUT_MILLION_TOKENS:.1f}",
            "workload_output_million_tokens": f"{OUTPUT_MILLION_TOKENS:.1f}",
            "standardized_api_cost_usd": f"{costs[model]:.4f}",
            "general_performance_score": f"{score:.10f}" if score is not None else NA,
            "performance_per_usd": f"{score / costs[model]:.10f}" if score is not None else NA,
            "pareto_frontier": str(model in frontier).lower() if score is not None else NA,
            "analysis_status": "included" if score is not None else "excluded_missing_performance_rank",
        })
    write_rows(
        output_dir / "performance_cost.csv",
        [
            "model_id", "model_name", "workload_input_million_tokens", "workload_output_million_tokens",
            "standardized_api_cost_usd", "general_performance_score", "performance_per_usd",
            "pareto_frontier", "analysis_status",
        ],
        value_rows,
    )

    budget_rows = []
    for budget in BUDGETS_USD:
        feasible = [model for model in ranked_ids if costs[model] <= budget]
        winner = max(feasible, key=lambda model: (performance[model], -costs[model])) if feasible else None
        budget_rows.append({
            "budget_usd_per_standardized_workload": f"{budget:.2f}",
            "feasible_ranked_models": str(len(feasible)),
            "recommended_model_id": winner or NA,
            "recommended_model_name": model_names[winner] if winner else NA,
            "performance_score": f"{performance[winner]:.10f}" if winner else NA,
            "cost_usd": f"{costs[winner]:.4f}" if winner else NA,
            "rule": "highest general TOPSIS score within budget; no missing-score model considered",
        })
    write_rows(
        output_dir / "budget_recommendations.csv",
        [
            "budget_usd_per_standardized_workload", "feasible_ranked_models", "recommended_model_id",
            "recommended_model_name", "performance_score", "cost_usd", "rule",
        ],
        budget_rows,
    )

    compatible = [row for row in attributes if row["efficiency_compatible"] == "true" and row["model_id"] in performance]
    ttft = {row["model_id"]: float(row["comparable_ttft_seconds"]) for row in compatible}
    speed = {row["model_id"]: float(row["comparable_output_speed_tokens_per_second"]) for row in compatible}
    latency = {row["model_id"]: float(row["comparable_total_latency_seconds"]) for row in compatible}
    ttft_score, speed_score, latency_score = minmax(ttft, False), minmax(speed, True), minmax(latency, False)
    engineering_rows = []
    for row in attributes:
        model = row["model_id"]
        if model in ttft_score:
            efficiency_score = (ttft_score[model] + speed_score[model] + latency_score[model]) / 3
            deployment_score = 0.7 * performance[model] + 0.3 * efficiency_score
            engineering_rows.append({
                "model_id": model, "model_name": row["model_name"],
                "ttft_benefit_score": f"{ttft_score[model]:.10f}",
                "speed_benefit_score": f"{speed_score[model]:.10f}",
                "latency_benefit_score": f"{latency_score[model]:.10f}",
                "engineering_efficiency_score": f"{efficiency_score:.10f}",
                "performance_score": f"{performance[model]:.10f}",
                "deployment_score_70p_performance_30p_efficiency": f"{deployment_score:.10f}",
                "analysis_status": "included_compatible_efficiency",
            })
        else:
            engineering_rows.append({
                "model_id": model, "model_name": row["model_name"],
                "ttft_benefit_score": NA, "speed_benefit_score": NA, "latency_benefit_score": NA,
                "engineering_efficiency_score": NA, "performance_score": f"{performance[model]:.10f}" if model in performance else NA,
                "deployment_score_70p_performance_30p_efficiency": NA,
                "analysis_status": "excluded_incompatible_efficiency" if model in performance else "excluded_missing_performance_and_efficiency",
            })
    write_rows(
        output_dir / "engineering_efficiency.csv",
        [
            "model_id", "model_name", "ttft_benefit_score", "speed_benefit_score", "latency_benefit_score",
            "engineering_efficiency_score", "performance_score", "deployment_score_70p_performance_30p_efficiency",
            "analysis_status",
        ],
        engineering_rows,
    )
    return {"frontier": sorted(frontier), "budget_rows": len(budget_rows), "efficiency_models": len(compatible)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        result = compute(args.output_dir)
    except (KeyError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Phase 6 complete: Pareto frontier={result['frontier']}; compatible efficiency models={result['efficiency_models']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
