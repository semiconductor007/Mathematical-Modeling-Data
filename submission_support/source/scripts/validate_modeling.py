"""Validate cross-phase modeling outputs and fail closed on inconsistent results."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_rows(relative: str) -> list[dict[str, str]]:
    path = ROOT / relative
    if not path.exists():
        raise ValueError(f"Missing output: {relative}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate() -> list[str]:
    issues: list[str] = []
    screening = read_rows("results/phase3/indicator_screening.csv")
    if len(screening) != 9 or any(row["phase3_decision"] != "retain" for row in screening):
        issues.append("Phase 3 must document nine retained indicators")

    weights = read_rows("results/phase4/critic_weights.csv")
    if len(weights) != 9 or abs(sum(float(row["critic_weight"]) for row in weights) - 1) > 1e-8:
        issues.append("CRITIC weights must contain nine indicators and sum to one")
    ranking = read_rows("results/phase4/general_ranking.csv")
    ranked = [row for row in ranking if row["ranking_status"] == "ranked_complete_case"]
    if sorted(int(row["rank"]) for row in ranked) != list(range(1, len(ranked) + 1)):
        issues.append("General ranks must be unique and consecutive")
    if len(ranked) != 5 or sum(row["ranking_status"] == "not_ranked_insufficient_coverage" for row in ranking) != 1:
        issues.append("General ranking must have five complete cases and one explicit exclusion")

    scenario_weights = read_rows("results/phase5/scenario_weights.csv")
    scenarios = {row["scenario"] for row in scenario_weights}
    if len(scenarios) != 3:
        issues.append("Exactly three scenarios are required")
    for scenario in scenarios:
        total = sum(float(row["combined_weight"]) for row in scenario_weights if row["scenario"] == scenario)
        if abs(total - 1) > 1e-8:
            issues.append(f"Scenario weights do not sum to one: {scenario}")

    cost = read_rows("results/phase6/performance_cost.csv")
    if not any(row["pareto_frontier"] == "true" for row in cost):
        issues.append("Performance-cost analysis has no Pareto model")
    budgets = read_rows("results/phase6/budget_recommendations.csv")
    for row in budgets:
        if row["recommended_model_id"] != "NA" and float(row["cost_usd"]) > float(row["budget_usd_per_standardized_workload"]):
            issues.append("Budget recommendation exceeds its budget")

    correlations = read_rows("results/phase7/rank_correlation.csv")
    if len(correlations) != 36:
        issues.append("Expected 36 weight perturbation scenarios")
    if any(not -1 <= float(row["kendall_tau_vs_baseline"]) <= 1 for row in correlations):
        issues.append("Kendall tau outside [-1, 1]")

    for name in ("general_ranking.svg", "critic_weights.svg", "scenario_rank_changes.svg", "performance_cost_pareto.svg"):
        path = ROOT / "figures" / name
        if not path.exists() or not path.read_text(encoding="utf-8").startswith("<svg"):
            issues.append(f"Missing or invalid figure: {name}")
    return issues


def main() -> int:
    try:
        issues = validate()
    except (KeyError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    if issues:
        print(f"Modeling validation failed: {len(issues)} issue(s).")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Modeling validation passed: Phases 3-7 outputs are internally consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
