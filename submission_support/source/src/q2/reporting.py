"""Generate Question 2 paper-writing material."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.q2.analysis import OBJECTIVE_SHARE, SCENARIO_LABELS


def generate_report(result: dict[str, object], docs_dir: Path) -> Path:
    docs_dir.mkdir(parents=True, exist_ok=True)
    rankings: pd.DataFrame = result["scenario_rankings"]  # type: ignore[assignment]
    weights: pd.DataFrame = result["scenario_weights"]  # type: ignore[assignment]
    changes: pd.DataFrame = result["rank_changes"]  # type: ignore[assignment]
    kimi: pd.DataFrame = result["kimi"]  # type: ignore[assignment]
    stability: pd.DataFrame = result["stability"]  # type: ignore[assignment]
    lines = [
        "# 问题2场景化评价结果摘要",
        "",
        "## 1. 建模方法及与问题1的衔接",
        "",
        "直接复用问题1的九项最终指标、Min–Max 标准化矩阵和 CRITIC 权重，不重新筛选、标准化或插补。严格按 `model(1).md` §3，采用 "
        f"$w^*_{'{s,j}'}={OBJECTIVE_SHARE}w_j+{1-OBJECTIVE_SHARE}a_{'{s,j}'}$ 组合赋权，再使用与问题1相同的 TOPSIS。GLM-5.2 因仅覆盖 4/9 项继续不参与完整矩阵排名。",
        "",
        "## 2. 三类场景权重",
        "",
    ]
    for scenario, label in SCENARIO_LABELS.items():
        group = weights.loc[weights["scenario"] == scenario].sort_values("combined_weight", ascending=False)
        top = "、".join(f"{row.metric}={row.combined_weight:.4f}" for row in group.head(3).itertuples())
        lines.append(f"- {label}：权重最高的三项为 {top}；权重和为 {group['combined_weight'].sum():.6f}。")
    for section, (scenario, label) in enumerate(SCENARIO_LABELS.items(), start=3):
        group = rankings.loc[(rankings["scenario"] == scenario) & (rankings["ranking_status"] == "ranked_complete_case")].sort_values("rank")
        lines += ["", f"## {section}. {label}排名", "", "| 排名 | 模型 | TOPSIS 得分 | 相对Q1名次变化 |", "|---:|---|---:|---:|"]
        for row in group.itertuples():
            lines.append(f"| {int(row.rank)} | {row.model} | {row.topsis_score:.10f} | {int(row.rank_improvement_vs_q1):+d} |")
    sensitive = changes.loc[changes["scenario_sensitivity"] == "场景敏感型"]
    stable = changes.loc[changes["scenario_sensitivity"] == "场景稳定型"]
    lines += [
        "",
        "## 6. 排名变化及机理",
        "",
        "场景敏感型模型为：" + ("、".join(sensitive["model"].tolist()) if not sensitive.empty else "无") + "；场景稳定型模型为：" + "、".join(stable["model"].tolist()) + "。",
        "科研场景提升 AA-LCR 与 CharXiv RQ 的组合权重，而 Kimi K3 在 AA-LCR、OmniDocBench 等指标上的标准化表现领先，使其由问题1第2升至科研场景第1。代码场景显著提升 SciCode 权重，Claude Fable 5 在该指标取全体最高标准化值，因此继续保持第1。日常场景提高 GDPval、MMMU-Pro 与 MathVision 权重，Claude Fable 5 的综合匹配度仍最高。以上权重变化和逐项乘积可在 `kimi_k3_scenario_analysis.csv` 追溯。",
        "",
        "## 7. Kimi K3场景表现",
        "",
    ]
    kimi_scenarios = kimi[["scenario", "scenario_name", "scenario_score", "scenario_rank"]].drop_duplicates()
    for row in kimi_scenarios.itertuples():
        lines.append(f"- {row.scenario_name}：得分 {row.scenario_score:.10f}，排名第 {int(row.scenario_rank)}。")
    best_rank = kimi_scenarios["scenario_rank"].min()
    best = "、".join(kimi_scenarios.loc[kimi_scenarios["scenario_rank"] == best_rank, "scenario_name"])
    worst_rank = kimi_scenarios["scenario_rank"].max()
    worst = "、".join(kimi_scenarios.loc[kimi_scenarios["scenario_rank"] == worst_rank, "scenario_name"])
    kimi_stability = stability.loc[stability["model_id"] == "kimi-k3"]
    lines += [
        f"最强场景为 {best}，最弱场景为 {worst}。这里按场景内名次判断，不把不同权重体系下的 TOPSIS 绝对值直接解释为跨场景效用大小。",
        "",
        "## 8. 稳健性",
        "",
        "严格沿用 `model(1).md` §5.2 的 9 项 CRITIC 权重逐项乘以 0.8、0.9、1.1、1.2 后归一化的 36 种扰动，并将扰动后的客观权重重新与固定场景主观权重按 0.5/0.5 组合。",
    ]
    for row in kimi_stability.itertuples():
        lines.append(f"- {row.scenario_name}：Kimi 平均排名 {row.mean_rank:.4f}，范围 {int(row.minimum_rank)}–{int(row.maximum_rank)}，Top3 概率 {row.top3_probability:.2%}，最低 Kendall τ={row.minimum_kendall_tau:.3f}。")
    lines += [
        "",
        "## 9. 可直接用于论文的结论",
        "",
        "固定模型能力不变时，场景需求通过组合权重改变理想解距离，从而改变排序。Kimi K3 的长上下文与文档能力与科研长文本场景最匹配；Claude Fable 5 在日常综合与代码开发场景保持首位。该结论是给定主观权重方案下的场景化比较，不应外推为所有用户的唯一选择。",
    ]
    path = docs_dir / "q2_results_summary.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
