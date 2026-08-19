"""Validate the complete Question 1 deliverable without changing source data."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

CSV_FILES = (
    "data_quality_report.csv",
    "normalized_data.csv",
    "pearson_correlation.csv",
    "spearman_correlation.csv",
    "high_correlation_pairs.csv",
    "selected_metrics.csv",
    "removed_metrics.csv",
    "final_indicator_system.csv",
    "critic_weights.csv",
    "topsis_ranking.csv",
    "kimi_k3_metric_analysis.csv",
    "sensitivity_analysis.csv",
    "rank_stability.csv",
)
PNG_FILES = (
    "pearson_heatmap.png",
    "spearman_heatmap.png",
    "critic_weights_bar.png",
    "topsis_ranking_bar.png",
    "kimi_k3_radar.png",
    "kimi_k3_gap.png",
)
DOC_FILES = (
    "data_dictionary.md",
    "q1_metric_selection.md",
    "q1_results_summary.md",
)


def validate(output_dir: Path, docs_dir: Path) -> list[str]:
    issues: list[str] = []
    for name in CSV_FILES:
        path = output_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            issues.append(f"missing or empty CSV: {path}")
    for name in DOC_FILES:
        path = docs_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            issues.append(f"missing or empty document: {path}")
    for name in PNG_FILES:
        path = output_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            issues.append(f"missing or empty PNG: {path}")
            continue
        try:
            with Image.open(path) as image:
                dpi = image.info.get("dpi", (0, 0))
                if image.format != "PNG":
                    issues.append(f"not a PNG: {path}")
                if min(dpi) < 299:
                    issues.append(f"PNG is below 300 dpi: {path} ({dpi})")
        except OSError as exc:
            issues.append(f"unreadable PNG: {path} ({exc})")

    if issues:
        return issues

    weights = pd.read_csv(output_dir / "critic_weights.csv", encoding="utf-8-sig")
    ranking = pd.read_csv(output_dir / "topsis_ranking.csv", encoding="utf-8-sig")
    normalized = pd.read_csv(output_dir / "normalized_data.csv", encoding="utf-8-sig")
    sensitivity = pd.read_csv(output_dir / "sensitivity_analysis.csv", encoding="utf-8-sig")
    stability = pd.read_csv(output_dir / "rank_stability.csv", encoding="utf-8-sig")

    if abs(float(weights["weight"].sum()) - 1.0) > 1e-10:
        issues.append("CRITIC weights do not sum to one")
    if len(weights) != 9 or weights["metric"].nunique() != 9:
        issues.append("final CRITIC weight table must contain 9 unique metrics")
    if ranking["model_id"].nunique() != 6:
        issues.append("TOPSIS table must contain 6 unique models")
    ranked = ranking.loc[ranking["ranking_status"] == "ranked_complete_case"]
    if len(ranked) != 5 or not ranked["topsis_score"].between(0, 1).all():
        issues.append("TOPSIS must rank 5 complete models with scores in [0, 1]")
    glm = ranking.loc[ranking["model_id"] == "glm-5.2"]
    if len(glm) != 1 or glm["rank"].notna().any():
        issues.append("GLM-5 must remain explicitly unranked because of incomplete coverage")
    metric_columns = [column for column in normalized if column not in {"model_id", "model"}]
    values = normalized[metric_columns].stack()
    if len(normalized) != 6 or len(metric_columns) != 9 or not values.between(0, 1).all():
        issues.append("normalized matrix must be 6 x 9 with observed values in [0, 1]")
    monte_carlo = sensitivity.loc[sensitivity["analysis_type"] == "monte_carlo_weight_perturbation"]
    if monte_carlo["iteration"].nunique() != 1000:
        issues.append("sensitivity analysis must contain 1000 Monte Carlo iterations")
    kimi = stability.loc[stability["model_id"] == "kimi-k3"]
    if len(kimi) != 1 or float(kimi.iloc[0]["top3_probability"]) < 0.95:
        issues.append("Kimi K3 Top3 stability is unexpectedly below 95%")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/q1")
    parser.add_argument("--docs-dir", type=Path, default=ROOT / "docs")
    args = parser.parse_args()
    issues = validate(args.output_dir, args.docs_dir)
    if issues:
        print("Question 1 validation failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"Question 1 validation passed: {len(CSV_FILES)} CSVs, {len(PNG_FILES)} PNGs, {len(DOC_FILES)} documents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
