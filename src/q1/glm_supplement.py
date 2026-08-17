"""GLM-5.2 supplemental analysis required by model(1).md section 2.6."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.q1.analysis import write_csv
from src.q1.visualization import configure_style, save

METRICS = {
    "gpqa_diamond": "GPQA Diamond",
    "aa_lcr": "AA-LCR",
    "scicode": "SciCode",
    "gdpval_aa_v2": "GDPval-AA v2",
}


def run_analysis(root: Path, output_dir: Path) -> dict[str, object]:
    matrix = pd.read_csv(root / "data/processed/core_benchmark_matrix.csv", encoding="utf-8-sig")
    raw = pd.read_csv(root / "data/raw/benchmark_scores.csv", encoding="utf-8-sig")
    names = matrix.set_index("model_id")["model_name"].to_dict()
    rows = []
    for metric, indicator in METRICS.items():
        values = matrix.set_index("model_id")[metric].dropna().astype(float)
        glm_value = float(values.loc["glm-5.2"])
        leader_id = str(values.idxmax())
        rank = int((values > glm_value).sum()) + 1
        rows.append({
            "metric": metric,
            "indicator": indicator,
            "glm_score": glm_value,
            "score_unit": "elo" if metric == "gdpval_aa_v2" else "percent",
            "rank_among_six": rank,
            "models_compared": len(values),
            "leader_model_id": leader_id,
            "leader_model": names[leader_id],
            "leader_score": float(values.loc[leader_id]),
            "gap_to_leader": float(values.loc[leader_id] - glm_value),
            "relative_gap_to_leader_percent": float(100 * (values.loc[leader_id] - glm_value) / values.loc[leader_id]),
            "comparison_scope": "frozen_main_cohort_directly_comparable",
        })
    comparison = pd.DataFrame(rows)
    official = raw.loc[
        (raw["model_id"] == "glm-5.2")
        & (raw["benchmark"] == "HLE-Full (no tools)")
        & (raw["source_name"] == "Z.ai GLM-5.2 official launch report")
    ].copy()
    if len(official) != 1 or float(official.iloc[0]["score"]) != 40.5:
        raise AssertionError("Expected one GLM-5.2 official HLE no-tools score of 40.5")
    hle = pd.DataFrame([{
        "model_id": "glm-5.2",
        "model": "GLM-5.2",
        "benchmark": "HLE-Full (no tools)",
        "official_score": 40.5,
        "score_unit": "percent",
        "source_name": official.iloc[0]["source_name"],
        "source_url": official.iloc[0]["source_url"],
        "test_setting": official.iloc[0]["test_setting"],
        "directly_comparable_to_frozen_cohort": False,
        "usage_rule": "qualitative_scale_reference_only; never fill frozen-cohort NA or assign rank",
    }])
    write_csv(comparison, output_dir / "glm_partial_comparison.csv")
    write_csv(hle, output_dir / "glm_official_hle_note.csv")
    return {"matrix": matrix, "comparison": comparison, "hle": hle, "names": names}


def generate_figure(result: dict[str, object], output_dir: Path) -> Path:
    configure_style()
    matrix: pd.DataFrame = result["matrix"]  # type: ignore[assignment]
    comparison: pd.DataFrame = result["comparison"]  # type: ignore[assignment]
    names: dict[str, str] = result["names"]  # type: ignore[assignment]
    model_order = matrix["model_id"].tolist()
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))
    for ax, (metric, indicator) in zip(axes.flat, METRICS.items()):
        values = matrix.set_index("model_id")[metric].reindex(model_order).astype(float)
        colors = ["#dc2626" if model == "glm-5.2" else "#94a3b8" for model in model_order]
        bars = ax.bar([names[model] for model in model_order], values, color=colors)
        glm_row = comparison.loc[comparison["metric"] == metric].iloc[0]
        ax.bar_label(bars, fmt="%.1f", padding=2, fontsize=8)
        ax.set_title(f"{indicator}（GLM 第{int(glm_row['rank_among_six'])}/{int(glm_row['models_compared'])}）")
        ax.tick_params(axis="x", rotation=24, labelsize=8)
        if metric == "gdpval_aa_v2":
            ax.axhline(1000, color="#2563eb", linestyle="--", linewidth=1.2, label="Human baseline=1000")
            ax.legend(fontsize=8)
            ax.set_ylabel("Elo")
        else:
            ax.set_ylabel("得分（%）")
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("GLM-5.2 四项可比文本能力局部定位", fontsize=18, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    path = output_dir / "glm_partial_comparison.png"
    save(fig, path)
    return path
