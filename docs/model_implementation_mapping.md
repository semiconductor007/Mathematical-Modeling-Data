# 建模方法—代码—结果映射

最高优先级方法规范为仓库根目录 `model(1).md` v1.1。

| 问题/步骤 | model 中的数学方法 | 代码文件 | 主要函数 | 输出文件 | 状态 |
|---|---|---|---|---|---|
| Q1 标准化 | 正/负向 Min–Max | `src/q1/analysis.py` | `minmax_normalize` | `results/q1/normalized_data.csv` | 已实现 |
| Q1 相关性与筛选 | Pearson + Spearman，语义复核 | `src/q1/analysis.py` | `correlation_matrices`, `select_metrics` | `results/q1/*correlation.csv`, `selected_metrics.csv` | 已实现；候选阈值按既有Q1任务为0.85，model §2.2 为0.9同维度删除门槛；最终均保留9项 |
| Q1 客观赋权 | CRITIC：标准差×冲突性 | `src/q1/analysis.py` | `critic_weights` | `results/q1/critic_weights.csv` | 已实现 |
| Q1 综合评价 | TOPSIS 正负理想解距离 | `src/q1/analysis.py` | `topsis_scores`, `full_ranking` | `results/q1/topsis_ranking.csv` | 已实现 |
| Q1 Kimi分析 | 单项位次与领先差距 | `src/q1/analysis.py` | `kimi_metric_analysis` | `results/q1/kimi_k3_metric_analysis.csv` | 已实现 |
| Q1 GLM-5.2补充评价 | 4项局部位次 + 独立HLE定性参照 | `src/q1/glm_supplement.py` | `run_analysis`, `generate_figure` | `results/phase4b/glm_partial_comparison.csv`, `glm_official_hle_note.csv` | 已实现；不插补、不分配综合排名 |
| Q2 组合赋权 | $w^*_{s,j}=0.5w_j+0.5a_{s,j}$ | `src/q2/analysis.py` | `combined_weights` | `results/q2/scenario_weights.csv` | 已实现 |
| Q2 场景TOPSIS | 组合权重替代CRITIC权重 | `src/q2/analysis.py` | `scenario_rankings`（复用Q1 `topsis_scores`） | `results/q2/*ranking.csv` | 已实现 |
| Q2 差异机理 | 权重变化×模型标准化值 | `src/q2/analysis.py` | `rank_change_analysis`, `contribution_analysis` | `rank_change_analysis.csv`, `kimi_k3_scenario_analysis.csv` | 已实现 |
| Q2 稳健性 | model §5.2 的36种客观权重扰动向场景组合传播 | `src/q2/analysis.py` | `sensitivity_analysis` | `scenario_sensitivity.csv`, `scenario_stability.csv` | 已实现 |
| Q3 标准成本 | $Cost=P_{in}+0.2P_{out}$ | `src/q3/analysis.py` | `cost_audit`, `performance_cost_table` | `cost_data_audit.csv`, `performance_cost.csv` | 已实现 |
| Q3 Pareto | 成本更低且性能更高的两两支配 | `src/q3/analysis.py` | `pareto_table` | `pareto_analysis.csv` | 已实现 |
| Q3 预算选型 | $\arg\max S_i, Cost_i\le B$ | `src/q3/analysis.py` | `budget_selection` | `budget_selection.csv` | 已实现 |
| Q3 成本规律 | $S=β_0+β_1\ln(Cost)$ 最小二乘 | `src/q3/analysis.py` | `regression` | `performance_cost_regression.csv` | 已实现 |
| Q3 工程效率 | 三项正向化等权，$Deploy=0.7S+0.3E$ | `src/q3/analysis.py` | `engineering_efficiency` | `deploy_scores.csv` | 已实现 |
| Q3 稳健性 | 36种权重扰动下重算前沿与预算推荐 | `src/q3/analysis.py` | `q3_sensitivity` | `sensitivity_analysis.csv` | 已实现 |
| 全局稳健性：熵权法 | 熵权重重跑TOPSIS并与CRITIC对照 | `scripts/analyze_phase7_robustness.py` | `entropy_weights`, `analyze` | `results/phase7/method_comparison.csv`, `weight_method_comparison.csv` | 已实现（输出名与model建议名不同） |
| 全局稳健性：逐项扰动 | 9指标×4因子，共36场景，Kendall τ | `scripts/analyze_phase7_robustness.py` | `kendall_tau`, `analyze` | `weight_perturbation_rankings.csv`, `rank_correlation.csv` | 已实现 |
| Q1–Q3 汇总 | 按 `model_id` 对齐全部评价 | `src/q3/analysis.py` | `final_summary` | `results/final_model_summary.csv` | 已实现 |

## 一致性说明

Q2、Q3 的公式、参数、参与模型范围与 `model(1).md` 一致。问题1保持用户确认后的主排名不变；其高相关候选复核阈值来自先前Q1任务（0.85），与 model §2.2 的0.9删除门槛存在表述差异，但两套规则都没有删除指标，因此Q2/Q3的输入矩阵、CRITIC权重和TOPSIS得分完全一致。GLM-5.2 Phase4b 已补充四项局部位次与独立HLE口径说明，但仍不插补或分配综合排名。model 中的3D图属于可选增强，本轮未生成。实现复用现有Q1的 NumPy/pandas/Matplotlib依赖，而非 model §10.5 偏好的纯标准库；这不改变数学口径。
