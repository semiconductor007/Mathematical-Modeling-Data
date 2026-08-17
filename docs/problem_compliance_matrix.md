# 原题要求—模型—论文—结果合规矩阵

原题归档：`references/problem/TJMML_B.pdf`（2 页）。本表以原题文字为准，逐项核对当前实现，避免只按二手任务说明完成建模。

| 原题要求 | 当前数学方法 | 代码与结果证据 | 论文位置 | 状态 | 尚需处理 |
|---|---|---|---|---|---|
| Q1：梳理潜在指标 | 17项候选池，经覆盖率、可比性、区分度和语义维度冻结9项 | `results/core_indicator_selection.csv`、`results/q1/final_indicator_system.csv` | §2–§3 | 已满足 | 最终排版时保留指标来源和筛选理由 |
| Q1：Pearson/Spearman相关性分析 | 两类相关系数，缺失值成对删除，高相关只进入语义复核 | `results/q1/*correlation.csv`、热力图 | §3 | 已满足 | 样本仅5–6，应保留小样本警示 |
| Q1：筛选关键指标并构建完整体系 | 9项全部保留，记录4组0.85阈值候选对 | `selected_metrics.csv`、`removed_metrics.csv`、`q1_metric_selection.md` | §3 | 已满足 | model文档0.9门槛与既有Q1的0.85候选门槛表述不同，但最终集合一致 |
| Q1：合理赋权并论证 | CRITIC客观赋权，标准差衡量对比强度、相关性衡量冲突性 | `critic_weights.csv` | §4.1 | 已满足 | 强调权重只对应当前样本 |
| Q1：综合打分与排名 | CRITIC-TOPSIS，5个完整模型排名，GLM不插补 | `topsis_ranking.csv` | §4.2 | 已满足 | 无 |
| Q1：Kimi K3优劣势 | 单项位次、均值比较、与领先者标准化差距 | `kimi_k3_metric_analysis.csv` | §4.3 | 已满足 | 无 |
| Q1：数据不足模型处理 | GLM-5.2四项局部位次；官方HLE独立口径仅定性参照 | `results/phase4b/*.csv`、`glm_partial_comparison.png` | §4.2补充 | 已补齐 | 不得给GLM虚构综合排名 |
| Q2：三类场景差异化评价 | CRITIC权重与固定场景偏好按0.5/0.5组合，再做TOPSIS | `results/q2/scenario_weights.csv`、三份排名 | §5 | 已满足 | 场景主观权重需作为透明假设陈述 |
| Q2：解释差异机理 | 跟踪权重变化与“标准化值×场景权重”的方向性影响 | `rank_change_analysis.csv`、`kimi_k3_scenario_analysis.csv` | §5 | 已满足 | 不把加权分量误称为TOPSIS得分的可加贡献 |
| Q3：综合性能—落地成本效益 | Q1得分作为性能；标准API工作负载成本；Pareto和预算约束 | `results/q3/performance_cost.csv`、`pareto_analysis.csv`、`budget_selection.csv` | §6 | 已满足 | 结论仅适用于1M输入+0.2M输出工作负载 |
| Q3：不同预算选型 | 预算内最大Q1得分，预算为6/10/12/16/20美元 | `budget_selection.csv` | §6 | 已满足 | GLM因无综合性能不进入推荐 |
| Q3：成本与性能潜在规律 | $S=\beta_0+\beta_1\ln(Cost)$探索性回归 | `performance_cost_regression.csv` | §7 | 已满足 | n=5、调整R²低，不做因果推断 |
| 题面：推理时延 | compatible配置下TTFT、输出速度、总延迟正向化 | `deploy_scores.csv` | §6 | 已满足（工程子分析） | 只有4个配置兼容模型 |
| 题面：算力消耗/电力能耗 | 数据可得性审计；未用参数量、时延或API价格冒充能耗 | `cost_data_audit.csv` 的 `energy_data_available=false` | §6.2、§8 | **公开同口径数据不足** | 若后续获得相同硬件、批大小、精度、输出长度下的J/token或kWh数据，再扩展；当前不得估算 |
| 补充说明：不得自行测评 | 全部使用官方报告、权威平台和标准Benchmark公开数据 | `data/sources/*.csv` | §2、参考文献 | 已满足 | 正文必须保留清晰URL与检索日期 |
| 补充说明：Kimi参考内容 | 使用Kimi K3官方报告作为候选与对照来源之一 | `benchmark_sources.csv` | §2、参考文献 | 已满足 | 避免把厂商报告当作唯一独立证据 |

## 当前结论

三问的核心数学任务均已实现。现阶段唯一无法量化闭合的题面变量是“算力能耗”：公开资料没有覆盖5个完整排名模型、相同硬件与推理设置的统一能耗测量。当前论文应把API成本定义为直接落地成本，把TTFT/输出速度/总延迟定义为工程效率指标，并把能耗列为数据局限；二者不能合并冒称“真实电力成本”。

## 最终提交前仍需外部输入

题目首页要求遵循《第一届天津市五校数学建模联赛格式规范》。该规范尚未进入仓库，因此当前只能生成内容完整的审阅稿；页数、封面、摘要长度、字号、匿名信息、参考文献样式和附件要求需在规范补充后最终校准。
