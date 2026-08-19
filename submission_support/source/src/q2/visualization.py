"""Paper-ready Question 2 visualizations."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.q1.visualization import configure_style, save
from src.q2.analysis import SCENARIO_LABELS


def rank_comparison(rankings: pd.DataFrame, q1: pd.DataFrame, path: Path) -> None:
    ranked_q1 = q1.loc[q1["ranking_status"] == "ranked_complete_case"]
    stages = ["问题1综合", *SCENARIO_LABELS.values()]
    scenarios = list(SCENARIO_LABELS)
    palette = {
        "claude-fable-5": "#2563eb",
        "kimi-k3": "#dc2626",
        "gpt-5.6-sol": "#f59e0b",
        "gpt-5.5": "#16a34a",
        "claude-opus-4.8": "#7c3aed",
    }
    fig, ax = plt.subplots(figsize=(11, 6.8))
    for item in ranked_q1.sort_values("rank").itertuples():
        ranks = [int(item.rank)] + [
            int(rankings.loc[(rankings["scenario"] == scenario) & (rankings["model_id"] == item.model_id), "rank"].iloc[0])
            for scenario in scenarios
        ]
        color = palette[item.model_id]
        ax.plot(stages, ranks, marker="o", linewidth=3 if item.model_id == "kimi-k3" else 1.8, label=item.model, color=color)
        for x, value in enumerate(ranks):
            ax.text(x, value - 0.10, str(value), ha="center", fontsize=9)
    ax.set_ylim(5.45, 0.55)
    ax.set_ylabel("排名（越高越好）")
    ax.set_title("问题1与三类场景排名变化")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    save(fig, path)


def heatmap(frame: pd.DataFrame, path: Path, value_column: str, title: str, fmt: str) -> None:
    pivot = frame.pivot(index="scenario_name", columns="model", values=value_column)
    order = [SCENARIO_LABELS[key] for key in SCENARIO_LABELS]
    pivot = pivot.reindex(order)
    fig, ax = plt.subplots(figsize=(10.5, 4.7))
    image = ax.imshow(pivot.to_numpy(float), cmap="YlGnBu", aspect="auto")
    ax.set_xticks(range(len(pivot.columns)), pivot.columns, rotation=20, ha="right")
    ax.set_yticks(range(len(pivot.index)), pivot.index)
    for y in range(len(pivot.index)):
        for x in range(len(pivot.columns)):
            value = pivot.iloc[y, x]
            ax.text(x, y, format(value, fmt), ha="center", va="center", color="white" if value > np.nanmean(pivot.to_numpy()) else "#111827")
    fig.colorbar(image, ax=ax, shrink=0.8)
    ax.set_title(title)
    fig.tight_layout()
    save(fig, path)


def rank_change(changes: pd.DataFrame, path: Path) -> None:
    labels = ["科研长文本", "日常对话", "代码开发"]
    columns = ["research_rank_change", "dialogue_rank_change", "coding_rank_change"]
    x = np.arange(len(changes))
    width = 0.24
    fig, ax = plt.subplots(figsize=(11, 6.3))
    for index, (label, column) in enumerate(zip(labels, columns)):
        # Positive means rank improved, so invert the stored new-minus-old change.
        ax.bar(x + (index - 1) * width, -changes[column], width, label=label)
    ax.axhline(0, color="#334155", linewidth=1)
    ax.set_xticks(x, changes["model"], rotation=18, ha="right")
    ax.set_ylabel("相对问题1排名提升（正值为上升）")
    ax.set_title("场景化评价对模型排名的影响")
    ax.legend()
    fig.tight_layout()
    save(fig, path)


def kimi_radar(kimi: pd.DataFrame, path: Path) -> None:
    metrics = kimi.loc[kimi["scenario"] == "research_long_text", "indicator"].tolist()
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(9, 8), subplot_kw={"polar": True})
    colors = ["#2563eb", "#16a34a", "#dc2626"]
    for color, (scenario, label) in zip(colors, SCENARIO_LABELS.items()):
        group = kimi.loc[kimi["scenario"] == scenario]
        values = group["weighted_normalized_component"].tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=2.3, color=color, label=label)
        ax.fill(angles, values, alpha=0.08, color=color)
    ax.set_xticks(angles[:-1], metrics)
    ax.set_ylim(0, max(0.25, float(kimi["weighted_normalized_component"].max()) * 1.12))
    ax.set_title("Kimi K3：标准化能力 × 场景组合权重", pad=25)
    ax.legend(bbox_to_anchor=(1.28, 1.10))
    fig.tight_layout()
    save(fig, path)


def weight_heatmap(weights: pd.DataFrame, path: Path) -> None:
    pivot = weights.pivot(index="scenario_name", columns="metric", values="combined_weight")
    order = [SCENARIO_LABELS[key] for key in SCENARIO_LABELS]
    pivot = pivot.reindex(order)
    fig, ax = plt.subplots(figsize=(12.5, 4.5))
    image = ax.imshow(pivot.to_numpy(float), cmap="OrRd", aspect="auto")
    ax.set_xticks(range(len(pivot.columns)), pivot.columns, rotation=28, ha="right")
    ax.set_yticks(range(len(pivot.index)), [f"{name}（Σ=1）" for name in pivot.index])
    for y in range(len(pivot.index)):
        for x in range(len(pivot.columns)):
            ax.text(x, y, f"{pivot.iloc[y, x]:.3f}", ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=ax, shrink=0.8, label="组合权重")
    ax.set_title("三类场景组合权重")
    fig.tight_layout()
    save(fig, path)


def generate_figures(result: dict[str, object], output_dir: Path) -> list[Path]:
    configure_style()
    paths = [
        output_dir / "scenario_rank_comparison.png",
        output_dir / "scenario_score_heatmap.png",
        output_dir / "rank_change.png",
        output_dir / "kimi_k3_scenario_radar.png",
        output_dir / "scenario_weights_heatmap.png",
    ]
    rankings: pd.DataFrame = result["scenario_rankings"]  # type: ignore[assignment]
    ranked = rankings.loc[rankings["ranking_status"] == "ranked_complete_case"]
    rank_comparison(rankings, result["q1_ranking"], paths[0])  # type: ignore[arg-type]
    heatmap(ranked, paths[1], "topsis_score", "三类场景 TOPSIS 得分", ".3f")
    rank_change(result["rank_changes"], paths[2])  # type: ignore[arg-type]
    kimi_radar(result["kimi"], paths[3])  # type: ignore[arg-type]
    weight_heatmap(result["scenario_weights"], paths[4])  # type: ignore[arg-type]
    return paths
