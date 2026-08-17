"""Paper-ready 300 dpi PNG figures for Question 1."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .analysis import DIMENSION_NAMES


def configure_style() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#334155",
        "axes.titleweight": "bold",
        "axes.grid": False,
    })


def save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def heatmap(matrix: pd.DataFrame, labels: list[str], title: str, path: Path) -> None:
    size = max(8.0, 0.82 * len(labels) + 2.2)
    fig, ax = plt.subplots(figsize=(size, size * 0.86))
    image = ax.imshow(matrix.to_numpy(dtype=float), cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(labels)), labels=labels, rotation=42, ha="right")
    ax.set_yticks(range(len(labels)), labels=labels)
    for i in range(len(labels)):
        for j in range(len(labels)):
            value = matrix.iloc[i, j]
            color = "white" if abs(value) >= 0.65 else "#172033"
            ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=8, color=color)
    ax.set_title(title, pad=16)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    colorbar.set_label("相关系数")
    fig.tight_layout()
    save(fig, path)


def horizontal_bar(labels: list[str], values: list[float], title: str, xlabel: str, path: Path, highlight: str | None = None) -> None:
    order = np.argsort(values)
    labels_ordered = [labels[index] for index in order]
    values_ordered = [values[index] for index in order]
    colors = ["#dc2626" if label == highlight else "#2563eb" for label in labels_ordered]
    fig, ax = plt.subplots(figsize=(9.2, max(4.8, 0.52 * len(labels) + 1.8)))
    bars = ax.barh(labels_ordered, values_ordered, color=colors, alpha=0.9)
    ax.bar_label(bars, labels=[f"{value:.4f}" for value in values_ordered], padding=4, fontsize=9)
    ax.set_title(title, pad=14)
    ax.set_xlabel(xlabel)
    ax.set_xlim(0, max(values_ordered) * 1.16 if values_ordered else 1)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, path)


def radar_chart(
    normalized: pd.DataFrame,
    weights: pd.DataFrame,
    dimensions: dict[str, str],
    ranking: pd.DataFrame,
    model_names: dict[str, str],
    path: Path,
) -> None:
    ranked = ranking.loc[ranking["ranking_status"] == "ranked_complete_case"].sort_values("rank")
    leader_id = str(ranked.iloc[0]["model_id"])
    complete_ids = ranked["model_id"].tolist()
    metric_weights = weights.set_index("metric")["weight"].to_dict()
    dimension_order = list(dict.fromkeys(dimensions.values()))

    def aggregate(model_id: str) -> list[float]:
        result = []
        for dimension in dimension_order:
            metric_list = [metric for metric, value in dimensions.items() if value == dimension]
            denom = sum(metric_weights[metric] for metric in metric_list)
            result.append(sum(normalized.loc[model_id, metric] * metric_weights[metric] for metric in metric_list) / denom)
        return result

    kimi = aggregate("kimi-k3")
    leader = aggregate(leader_id)
    average = np.mean([aggregate(model_id) for model_id in complete_ids], axis=0).tolist()
    labels = [DIMENSION_NAMES[item] for item in dimension_order]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(9, 8), subplot_kw={"polar": True})
    for values, label, color, width in (
        (kimi, "Kimi K3", "#dc2626", 2.7),
        (leader, model_names[leader_id], "#2563eb", 2.2),
        (average, "完整模型均值", "#64748b", 1.8),
    ):
        closed = values + values[:1]
        ax.plot(angles, closed, color=color, linewidth=width, label=label)
        ax.fill(angles, closed, color=color, alpha=0.07)
    ax.set_xticks(angles[:-1], labels, fontsize=9)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=8)
    ax.set_title("Kimi K3 一级能力维度对比", pad=24)
    ax.legend(loc="upper right", bbox_to_anchor=(1.28, 1.14), frameon=False)
    fig.tight_layout()
    save(fig, path)


def gap_chart(kimi: pd.DataFrame, path: Path) -> None:
    frame = kimi.sort_values("gap_to_leader_normalized", ascending=True)
    colors = frame["assessment"].map({"advantage": "#16a34a", "middle": "#64748b", "weakness": "#dc2626"}).tolist()
    fig, ax = plt.subplots(figsize=(9.4, 6.4))
    bars = ax.barh(frame["indicator"], frame["gap_to_leader_normalized"], color=colors)
    ax.bar_label(bars, labels=[f"{value:.3f}" for value in frame["gap_to_leader_normalized"]], padding=4, fontsize=9)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("与该指标最优模型的标准化差距（越小越好）")
    ax.set_title("Kimi K3 单指标差距")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, path)


def generate_figures(result: dict[str, object], output_dir: Path) -> list[Path]:
    configure_style()
    metric_names: dict[str, str] = result["metric_names"]  # type: ignore[assignment]
    metrics: list[str] = result["metrics"]  # type: ignore[assignment]
    labels = [metric_names[item] for item in metrics]
    paths = [
        output_dir / "pearson_heatmap.png",
        output_dir / "spearman_heatmap.png",
        output_dir / "critic_weights_bar.png",
        output_dir / "topsis_ranking_bar.png",
        output_dir / "kimi_k3_radar.png",
        output_dir / "kimi_k3_gap.png",
    ]
    heatmap(result["pearson"], labels, "问题1指标 Pearson 相关性", paths[0])  # type: ignore[arg-type]
    heatmap(result["spearman"], labels, "问题1指标 Spearman 相关性", paths[1])  # type: ignore[arg-type]
    weights: pd.DataFrame = result["weights"]  # type: ignore[assignment]
    horizontal_bar(weights["indicator"].tolist(), weights["weight"].tolist(), "CRITIC 客观权重", "权重", paths[2])
    ranking: pd.DataFrame = result["ranking"]  # type: ignore[assignment]
    ranked = ranking.loc[ranking["ranking_status"] == "ranked_complete_case"]
    horizontal_bar(
        ranked["model"].tolist(), ranked["topsis_score"].tolist(),
        "CRITIC–TOPSIS 综合性能排名", "TOPSIS 相对接近度", paths[3], highlight="Kimi K3",
    )
    radar_chart(
        result["normalized"], weights, result["dimensions"], ranking,
        result["model_names"], paths[4],  # type: ignore[arg-type]
    )
    gap_chart(result["kimi"], paths[5])  # type: ignore[arg-type]
    return paths
