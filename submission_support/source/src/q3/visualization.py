"""Paper-ready Question 3 visualizations."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.q1.visualization import configure_style, save


def pareto_plot(frame: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 6.5))
    dominated = frame.loc[~frame["is_pareto_frontier"]]
    frontier = frame.loc[frame["is_pareto_frontier"]].sort_values("standard_workload_cost_usd")
    ax.scatter(dominated["standard_workload_cost_usd"], dominated["q1_performance_score"], s=90, color="#94a3b8", label="被支配模型")
    ax.plot(frontier["standard_workload_cost_usd"], frontier["q1_performance_score"], color="#dc2626", linewidth=2.2, marker="o", markersize=10, label="Pareto 前沿")
    for row in frame.itertuples():
        ax.annotate(row.model, (row.standard_workload_cost_usd, row.q1_performance_score), xytext=(6, 7), textcoords="offset points")
    ax.set_xlim(left=0)
    ax.set_xlabel("标准工作负载成本（USD）")
    ax.set_ylabel("问题1 TOPSIS 综合性能")
    ax.set_title("大模型性能—成本 Pareto 前沿")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    save(fig, path)


def budget_plot(frame: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    ax.step(frame["budget_limit_usd"], frame["performance"], where="post", linewidth=2.5, color="#2563eb")
    ax.scatter(frame["budget_limit_usd"], frame["performance"], s=70, color="#dc2626", zorder=3)
    for row in frame.itertuples():
        ax.annotate(row.recommended_model, (row.budget_limit_usd, row.performance), xytext=(4, 9), textcoords="offset points", fontsize=9)
    ax.set_xticks(frame["budget_limit_usd"])
    ax.set_ylim(0, 0.82)
    ax.set_xlabel("预算上限（USD / 标准工作负载）")
    ax.set_ylabel("推荐模型的Q1性能得分")
    ax.set_title("预算约束下的最优模型选择")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    save(fig, path)


def regression_plot(frame: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    ax.scatter(frame["standard_workload_cost_usd"], frame["q1_performance_score"], s=100, color="#2563eb")
    for row in frame.itertuples():
        ax.annotate(row.model, (row.standard_workload_cost_usd, row.q1_performance_score), xytext=(5, 7), textcoords="offset points")
    costs = np.linspace(float(frame["standard_workload_cost_usd"].min()), float(frame["standard_workload_cost_usd"].max()), 200)
    first = frame.iloc[0]
    fit = first["intercept"] + first["slope_log_cost"] * np.log(costs)
    ax.plot(costs, fit, color="#dc2626", linewidth=2.2, label="对数拟合")
    ax.text(
        0.03, 0.95,
        f"S = {first['intercept']:.4f} + {first['slope_log_cost']:.4f} ln(Cost)\n$R^2$ = {first['r_squared']:.4f}, RMSE = {first['rmse']:.4f}",
        transform=ax.transAxes, va="top", bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "#cbd5e1"},
    )
    ax.set_xlim(left=0)
    ax.set_xlabel("标准工作负载成本（USD）")
    ax.set_ylabel("问题1 TOPSIS 综合性能")
    ax.set_title("成本—性能对数回归（探索性，n=5）")
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    save(fig, path)


def efficiency_plot(frame: pd.DataFrame, path: Path) -> None:
    included = frame.loc[frame["analysis_status"] == "included_compatible_efficiency"].copy()
    columns = ["ttft_benefit_score", "speed_benefit_score", "latency_benefit_score", "deployment_score"]
    labels = ["TTFT正向化", "输出速度正向化", "总延迟正向化", "部署综合分"]
    x = np.arange(len(included))
    width = 0.19
    fig, ax = plt.subplots(figsize=(11, 6.3))
    for index, (column, label) in enumerate(zip(columns, labels)):
        ax.bar(x + (index - 1.5) * width, included[column], width, label=label)
    ax.set_xticks(x, included["model"], rotation=15, ha="right")
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("标准化得分")
    ax.set_title("兼容配置模型的工程效率与部署综合分")
    ax.legend(ncols=2)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    save(fig, path)


def generate_figures(result: dict[str, object], output_dir: Path) -> list[Path]:
    configure_style()
    paths = [
        output_dir / "performance_cost_pareto.png",
        output_dir / "budget_selection.png",
        output_dir / "performance_cost_fit.png",
        output_dir / "engineering_efficiency.png",
    ]
    pareto_plot(result["pareto"], paths[0])  # type: ignore[arg-type]
    budget_plot(result["budgets"], paths[1])  # type: ignore[arg-type]
    regression_plot(result["regression"], paths[2])  # type: ignore[arg-type]
    efficiency_plot(result["engineering"], paths[3])  # type: ignore[arg-type]
    return paths
