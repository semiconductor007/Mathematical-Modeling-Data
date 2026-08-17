"""Question 3 report and model-to-code traceability mapping."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.q3.analysis import BUDGETS, INPUT_MILLION_TOKENS, OUTPUT_MILLION_TOKENS


def generate_report(result: dict[str, object], docs_dir: Path) -> Path:
    docs_dir.mkdir(parents=True, exist_ok=True)
    audit: pd.DataFrame = result["audit"]  # type: ignore[assignment]
    value: pd.DataFrame = result["performance_cost"]  # type: ignore[assignment]
    pareto: pd.DataFrame = result["pareto"]  # type: ignore[assignment]
    budgets: pd.DataFrame = result["budgets"]  # type: ignore[assignment]
    regression: pd.DataFrame = result["regression"]  # type: ignore[assignment]
    engineering: pd.DataFrame = result["engineering"]  # type: ignore[assignment]
    kimi: pd.Series = result["kimi"].iloc[0]  # type: ignore[index,union-attr]
    sensitivity: pd.DataFrame = result["sensitivity"]  # type: ignore[assignment]
    included = value.loc[value["analysis_status"] == "included_ranked_model"].sort_values("performance_per_usd", ascending=False)
    fit = regression.iloc[0]
    frontier_names = "、".join(pareto.loc[pareto["is_pareto_frontier"], "model"])
    lines = [
        "# 问题3性能—成本效益结果摘要",
        "",
        "## 1. 建模方法",
        "",
        "严格按 `model(1).md` §4：直接采用问题1 TOPSIS 得分作为性能，定义标准工作负载，进行性能—成本 Pareto 判定、预算约束选型、对数回归，以及兼容配置模型的工程效率和 0.7/0.3 部署综合评价。",
        "",
        "## 2. 成本数据与假设",
        "",
        f"标准工作负载为 {INPUT_MILLION_TOKENS:.1f} 百万输入 token + {OUTPUT_MILLION_TOKENS:.1f} 百万输出 token；成本公式为 `输入单价×1 + 输出单价×0.2`，单位统一为 USD。6 个最终模型价格均完整，兼容效率记录为 {int(audit['efficiency_compatible'].sum())}/6。仓库没有可比能耗字段，因此未估算能耗。",
        "",
        "## 3. 性能成本评价",
        "",
        "| 模型 | Q1性能 | 标准成本 | 性能/美元 | 性价比排名 |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in included.itertuples():
        lines.append(f"| {row.model} | {row.q1_performance_score:.10f} | ${row.standard_workload_cost_usd:.3f} | {row.performance_per_usd:.6f} | {int(row.value_rank_among_ranked)} |")
    lines += [
        "",
        "## 4. Pareto前沿",
        "",
        f"Pareto 前沿模型为：{frontier_names}。被支配模型及其支配者记录在 `pareto_analysis.csv`，只有5个问题1完整排名模型参与判定。GLM-5.2 的标准成本为 $1.918，但没有完整Q1性能得分，只作低价文本模型参照，不进入前沿。",
        "",
        "## 5. 预算选型",
        "",
        "| 预算上限 | 可选模型数 | 推荐模型 | 性能 | 实际成本 |",
        "|---:|---:|---|---:|---:|",
    ]
    for row in budgets.itertuples():
        lines.append(f"| ${row.budget_limit_usd:.0f} | {row.feasible_models} | {row.recommended_model} | {row.performance:.10f} | ${row.cost_usd:.3f} |")
    lines += [
        "",
        "## 6. 性能成本关系",
        "",
        f"探索性回归为 $S={fit['intercept']:.6f}+{fit['slope_log_cost']:.6f}\\ln(Cost)$，$R^2={fit['r_squared']:.6f}$，调整 $R^2={fit['adjusted_r_squared']:.6f}$，RMSE={fit['rmse']:.6f}。样本仅5个且拟合度偏低，最多说明本样本中价格与性能的正相关较弱；不能推断因果或普遍边际规律。",
        "",
        "## 7. 工程效率",
        "",
    ]
    for row in engineering.loc[engineering["analysis_status"] == "included_compatible_efficiency"].sort_values("deployment_rank").itertuples():
        lines.append(f"- {row.model}：效率分 {row.engineering_efficiency_score:.6f}，部署综合分 {row.deployment_score:.6f}，部署排名第 {int(row.deployment_rank)}。")
    lines += [
        "",
        "## 8. Kimi K3成本效益定位",
        "",
        f"Kimi K3 的Q1性能为 {kimi['q1_performance_score']:.10f}（第{int(kimi['q1_rank'])}），标准成本 ${kimi['standard_workload_cost_usd']:.3f}，在完整排名模型中成本并列第{int(kimi['cost_rank_among_ranked'])}、性能/美元第{int(kimi['value_rank_among_ranked'])}，位于 Pareto 前沿。预算 6/10/12/16 美元时均推荐 Kimi K3；预算达到20美元后推荐 Claude Fable 5。与同价 GPT-5.5 相比，Kimi 性能更高并直接支配后者。",
        "",
        "## 9. 稳健性",
        "",
        "沿用 `model(1).md` §5.2 的36个 CRITIC 权重扰动场景，逐次重算问题1性能、Pareto和预算推荐。",
        f"Kimi K3 保持 Pareto 前沿的比例为 {sensitivity['kimi_on_pareto_frontier'].mean():.2%}，排名范围 {int(sensitivity['kimi_rank'].min())}–{int(sensitivity['kimi_rank'].max())}。",
    ]
    for budget in BUDGETS:
        column = f"budget_{int(budget)}_recommendation"
        dominant = sensitivity[column].value_counts(normalize=True)
        model_id, probability = dominant.index[0], dominant.iloc[0]
        lines.append(f"- ${budget:.0f} 预算：最常推荐 {model_id}，稳定率 {probability:.2%}。")
    lines += [
        "",
        "## 10. 局限与论文结论",
        "",
        "成本结论依赖固定 token 比例及公开标价，不含缓存、批处理、折扣、峰谷价和内部部署成本；效率分析只有4个兼容模型；无能耗数据；回归 n=5。给定这些边界，Kimi K3 是中低预算下的高性能高性价比选择，Claude Fable 5 是预算充足时的纯性能优先选择。",
    ]
    path = docs_dir / "q3_results_summary.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def generate_mapping(docs_dir: Path) -> Path:
    lines = [
        "# 建模方法—代码—结果映射",
        "",
        "最高优先级方法规范为仓库根目录 `model(1).md` v1.1。",
        "",
        "| 问题/步骤 | model 中的数学方法 | 代码文件 | 主要函数 | 输出文件 | 状态 |",
        "|---|---|---|---|---|---|",
        "| Q1 标准化 | 正/负向 Min–Max | `src/q1/analysis.py` | `minmax_normalize` | `results/q1/normalized_data.csv` | 已实现 |",
        "| Q1 相关性与筛选 | Pearson + Spearman，语义复核 | `src/q1/analysis.py` | `correlation_matrices`, `select_metrics` | `results/q1/*correlation.csv`, `selected_metrics.csv` | 已实现；候选阈值按既有Q1任务为0.85，model §2.2 为0.9同维度删除门槛；最终均保留9项 |",
        "| Q1 客观赋权 | CRITIC：标准差×冲突性 | `src/q1/analysis.py` | `critic_weights` | `results/q1/critic_weights.csv` | 已实现 |",
        "| Q1 综合评价 | TOPSIS 正负理想解距离 | `src/q1/analysis.py` | `topsis_scores`, `full_ranking` | `results/q1/topsis_ranking.csv` | 已实现 |",
        "| Q1 Kimi分析 | 单项位次与领先差距 | `src/q1/analysis.py` | `kimi_metric_analysis` | `results/q1/kimi_k3_metric_analysis.csv` | 已实现 |",
        "| Q1 GLM-5.2补充评价 | 4项局部位次 + 独立HLE定性参照 | `src/q1/glm_supplement.py` | `run_analysis`, `generate_figure` | `results/phase4b/glm_partial_comparison.csv`, `glm_official_hle_note.csv` | 已实现；不插补、不分配综合排名 |",
        "| Q2 组合赋权 | $w^*_{s,j}=0.5w_j+0.5a_{s,j}$ | `src/q2/analysis.py` | `combined_weights` | `results/q2/scenario_weights.csv` | 已实现 |",
        "| Q2 场景TOPSIS | 组合权重替代CRITIC权重 | `src/q2/analysis.py` | `scenario_rankings`（复用Q1 `topsis_scores`） | `results/q2/*ranking.csv` | 已实现 |",
        "| Q2 差异机理 | 权重变化×模型标准化值 | `src/q2/analysis.py` | `rank_change_analysis`, `contribution_analysis` | `rank_change_analysis.csv`, `kimi_k3_scenario_analysis.csv` | 已实现 |",
        "| Q2 稳健性 | model §5.2 的36种客观权重扰动向场景组合传播 | `src/q2/analysis.py` | `sensitivity_analysis` | `scenario_sensitivity.csv`, `scenario_stability.csv` | 已实现 |",
        "| Q3 标准成本 | $Cost=P_{in}+0.2P_{out}$ | `src/q3/analysis.py` | `cost_audit`, `performance_cost_table` | `cost_data_audit.csv`, `performance_cost.csv` | 已实现 |",
        "| Q3 Pareto | 成本更低且性能更高的两两支配 | `src/q3/analysis.py` | `pareto_table` | `pareto_analysis.csv` | 已实现 |",
        "| Q3 预算选型 | $\\arg\\max S_i, Cost_i\\le B$ | `src/q3/analysis.py` | `budget_selection` | `budget_selection.csv` | 已实现 |",
        "| Q3 成本规律 | $S=β_0+β_1\\ln(Cost)$ 最小二乘 | `src/q3/analysis.py` | `regression` | `performance_cost_regression.csv` | 已实现 |",
        "| Q3 工程效率 | 三项正向化等权，$Deploy=0.7S+0.3E$ | `src/q3/analysis.py` | `engineering_efficiency` | `deploy_scores.csv` | 已实现 |",
        "| Q3 稳健性 | 36种权重扰动下重算前沿与预算推荐 | `src/q3/analysis.py` | `q3_sensitivity` | `sensitivity_analysis.csv` | 已实现 |",
        "| 全局稳健性：熵权法 | 熵权重重跑TOPSIS并与CRITIC对照 | `scripts/analyze_phase7_robustness.py` | `entropy_weights`, `analyze` | `results/phase7/method_comparison.csv`, `weight_method_comparison.csv` | 已实现（输出名与model建议名不同） |",
        "| 全局稳健性：逐项扰动 | 9指标×4因子，共36场景，Kendall τ | `scripts/analyze_phase7_robustness.py` | `kendall_tau`, `analyze` | `weight_perturbation_rankings.csv`, `rank_correlation.csv` | 已实现 |",
        "| Q1–Q3 汇总 | 按 `model_id` 对齐全部评价 | `src/q3/analysis.py` | `final_summary` | `results/final_model_summary.csv` | 已实现 |",
        "",
        "## 一致性说明",
        "",
        "Q2、Q3 的公式、参数、参与模型范围与 `model(1).md` 一致。问题1保持用户确认后的主排名不变；其高相关候选复核阈值来自先前Q1任务（0.85），与 model §2.2 的0.9删除门槛存在表述差异，但两套规则都没有删除指标，因此Q2/Q3的输入矩阵、CRITIC权重和TOPSIS得分完全一致。GLM-5.2 Phase4b 已补充四项局部位次与独立HLE口径说明，但仍不插补或分配综合排名。model 中的3D图属于可选增强，本轮未生成。实现复用现有Q1的 NumPy/pandas/Matplotlib依赖，而非 model §10.5 偏好的纯标准库；这不改变数学口径。",
    ]
    path = docs_dir / "model_implementation_mapping.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
