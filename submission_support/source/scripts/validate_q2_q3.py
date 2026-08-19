"""Validate Question 2 and Question 3 deliverables and mathematical invariants."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
Q2_CSV = (
    "scenario_weights.csv", "scenario_rankings.csv", "research_ranking.csv", "dialogue_ranking.csv",
    "coding_ranking.csv", "rank_change_analysis.csv", "kimi_k3_scenario_analysis.csv",
    "scenario_sensitivity.csv", "scenario_stability.csv",
)
Q2_PNG = (
    "scenario_rank_comparison.png", "scenario_score_heatmap.png", "rank_change.png",
    "kimi_k3_scenario_radar.png", "scenario_weights_heatmap.png",
)
Q3_CSV = (
    "cost_data_audit.csv", "performance_cost.csv", "pareto_analysis.csv", "budget_selection.csv",
    "performance_cost_regression.csv", "deploy_scores.csv", "kimi_k3_cost_analysis.csv", "sensitivity_analysis.csv",
)
Q3_PNG = ("performance_cost_pareto.png", "budget_selection.png", "performance_cost_fit.png", "engineering_efficiency.png")
DOCS = ("q2_results_summary.md", "q3_results_summary.md", "model_implementation_mapping.md")


def validate_png(path: Path, issues: list[str]) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        issues.append(f"missing or empty PNG: {path}")
        return
    try:
        with Image.open(path) as image:
            dpi = image.info.get("dpi", (0, 0))
            if image.format != "PNG" or min(dpi) < 299:
                issues.append(f"invalid PNG format or DPI: {path} ({image.format}, {dpi})")
    except OSError as exc:
        issues.append(f"unreadable PNG: {path} ({exc})")


def validate(q2_dir: Path, q3_dir: Path, docs_dir: Path, summary_path: Path) -> list[str]:
    issues: list[str] = []
    for directory, names in ((q2_dir, Q2_CSV), (q3_dir, Q3_CSV)):
        for name in names:
            path = directory / name
            if not path.is_file() or path.stat().st_size == 0:
                issues.append(f"missing or empty CSV: {path}")
    for directory, names in ((q2_dir, Q2_PNG), (q3_dir, Q3_PNG)):
        for name in names:
            validate_png(directory / name, issues)
    for name in DOCS:
        path = docs_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            issues.append(f"missing or empty document: {path}")
    if not summary_path.is_file() or summary_path.stat().st_size == 0:
        issues.append(f"missing final summary: {summary_path}")
    if issues:
        return issues

    weights = pd.read_csv(q2_dir / "scenario_weights.csv", encoding="utf-8-sig")
    rankings = pd.read_csv(q2_dir / "scenario_rankings.csv", encoding="utf-8-sig")
    q2_sensitivity = pd.read_csv(q2_dir / "scenario_sensitivity.csv", encoding="utf-8-sig")
    totals = weights.groupby("scenario")["combined_weight"].sum()
    if len(totals) != 3 or not np.allclose(totals.to_numpy(), 1.0, atol=1e-10):
        issues.append("Q2 must contain three scenario weight vectors summing to one")
    ranked = rankings.loc[rankings["ranking_status"] == "ranked_complete_case"]
    if not (ranked.groupby("scenario")["model_id"].nunique() == 5).all():
        issues.append("Q2 must rank exactly five complete models in each scenario")
    if not ranked["topsis_score"].between(0, 1).all():
        issues.append("Q2 TOPSIS scores must be within [0, 1]")
    glm = rankings.loc[rankings["model_id"] == "glm-5.2"]
    if len(glm) != 3 or glm["rank"].notna().any():
        issues.append("GLM-5.2 must remain unranked in all Q2 scenarios")
    if len(q2_sensitivity) != 540 or q2_sensitivity[["scenario", "perturbed_metric", "factor"]].drop_duplicates().shape[0] != 108:
        issues.append("Q2 sensitivity must contain 36 perturbations x 3 scenarios x 5 models")

    audit = pd.read_csv(q3_dir / "cost_data_audit.csv", encoding="utf-8-sig")
    value = pd.read_csv(q3_dir / "performance_cost.csv", encoding="utf-8-sig")
    pareto = pd.read_csv(q3_dir / "pareto_analysis.csv", encoding="utf-8-sig")
    budgets = pd.read_csv(q3_dir / "budget_selection.csv", encoding="utf-8-sig")
    regression = pd.read_csv(q3_dir / "performance_cost_regression.csv", encoding="utf-8-sig")
    q3_sensitivity = pd.read_csv(q3_dir / "sensitivity_analysis.csv", encoding="utf-8-sig")
    summary = pd.read_csv(summary_path, encoding="utf-8-sig")
    expected_cost = audit["input_price_usd_per_million"] + 0.2 * audit["output_price_usd_per_million"]
    if len(audit) != 6 or not np.allclose(expected_cost, audit["standard_workload_cost_usd"]):
        issues.append("Q3 standard cost must equal input price + 0.2 x output price for six models")
    included = value.loc[value["analysis_status"] == "included_ranked_model"]
    if len(included) != 5 or not included["q1_performance_score"].between(0, 1).all():
        issues.append("Q3 must use five valid Q1 performance scores")
    for row in budgets.itertuples():
        if row.cost_usd > row.budget_limit_usd + 1e-10:
            issues.append(f"budget recommendation violates constraint at {row.budget_limit_usd}")
    for item in pareto.itertuples():
        others = pareto.loc[pareto["model_id"] != item.model_id]
        dominated = (
            (others["standard_workload_cost_usd"] <= item.standard_workload_cost_usd)
            & (others["q1_performance_score"] >= item.q1_performance_score)
            & ((others["standard_workload_cost_usd"] < item.standard_workload_cost_usd) | (others["q1_performance_score"] > item.q1_performance_score))
        ).any()
        if bool(item.is_pareto_frontier) == bool(dominated):
            issues.append(f"incorrect Pareto status for {item.model_id}")
    if regression["sample_size"].nunique() != 1 or int(regression["sample_size"].iloc[0]) != 5:
        issues.append("Q3 regression must use the five ranked models")
    if len(q3_sensitivity) != 36:
        issues.append("Q3 sensitivity must contain 36 model-specified perturbations")
    if len(summary) != 6 or summary["model_id"].nunique() != 6:
        issues.append("final_model_summary.csv must contain six unique models")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--q2-dir", type=Path, default=ROOT / "results/q2")
    parser.add_argument("--q3-dir", type=Path, default=ROOT / "results/q3")
    parser.add_argument("--docs-dir", type=Path, default=ROOT / "docs")
    parser.add_argument("--summary", type=Path, default=ROOT / "results/final_model_summary.csv")
    args = parser.parse_args()
    issues = validate(args.q2_dir, args.q3_dir, args.docs_dir, args.summary)
    if issues:
        print("Q2/Q3 validation failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"Q2/Q3 validation passed: {len(Q2_CSV)+len(Q3_CSV)+1} CSVs, {len(Q2_PNG)+len(Q3_PNG)} PNGs, {len(DOCS)} documents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
