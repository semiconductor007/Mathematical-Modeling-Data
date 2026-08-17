# 论文最终事实与提交核对清单

> 审计基准：`origin/main` / `deb6a35815a4bc9f2a1bd05322824ae5603cb798`
> 本文件只固化论文可引用的最终事实、来源映射和提交前检查项；不得据此修改 `raw/processed/results`。如结果流水线以后发生正式变更，必须重新核对本文件。

## 一、最终唯一事实

### 1. 模型池

- 初始候选 9 个；`final` 6 个；`excluded` 3 个。
- Final：`kimi-k3`、`gpt-5.6-sol`、`claude-fable-5`、`claude-opus-4.8`、`gpt-5.5`、`glm-5.2`。
- Excluded：
  - `gemini-3.1-pro-preview`：preview 状态且严格可比核心覆盖不足；
  - `deepseek-v4-pro-0813`：距截止日仅 4 天公开，分项覆盖不足；
  - `qwen3.8-2.4t-a95b`：距截止日仅 5 天公开，分项覆盖不足。
- 选择逻辑必须同时表述主流代表性、发布时间、exact version、公开可获得性、严格可比覆盖和数据截止日。75% 是指标筛选约束之一，不是倒推缩小模型池的唯一目的。

### 2. 九个核心指标

| 指标 | 覆盖 | 缺失模型 |
|---|---:|---|
| GPQA Diamond | 6/6（100.0%） | 无 |
| HLE-Full（no tools） | 5/6（83.3%） | GLM-5.2 |
| AA-LCR | 6/6（100.0%） | 无 |
| SciCode | 6/6（100.0%） | 无 |
| GDPval-AA v2 | 6/6（100.0%） | 无 |
| MMMU-Pro（no tools） | 5/6（83.3%） | GLM-5.2 |
| OmniDocBench | 5/6（83.3%） | GLM-5.2 |
| CharXiv RQ（no tools） | 5/6（83.3%） | GLM-5.2 |
| MathVision（no tools） | 5/6（83.3%） | GLM-5.2 |

### 3. CRITIC 权重

| 指标 | 最终权重 |
|---|---:|
| GPQA Diamond | 0.1039085788 |
| HLE-Full | 0.2013184129 |
| AA-LCR | 0.1269683755 |
| SciCode | 0.0673656510 |
| GDPval-AA v2 | 0.1167204353 |
| MMMU-Pro | 0.0865041663 |
| OmniDocBench | 0.1482615325 |
| CharXiv RQ | 0.0733538394 |
| MathVision | 0.0755990084 |

CSV 十位小数加总为 `1.0000000001`，属于舍入误差。

### 4. 通用 TOPSIS 主排名

| 排名 | 模型 | closeness score |
|---:|---|---:|
| 1 | Claude Fable 5 | 0.7253547227 |
| 2 | Kimi K3 | 0.5933487598 |
| 3 | GPT-5.6 Sol | 0.5177743845 |
| 4 | GPT-5.5 | 0.4409692387 |
| 5 | Claude Opus 4.8 | 0.3901637084 |

GLM-5.2 只有 4/9 项核心成绩，`topsis_score=NA`，不得进入主排名或写成“排名第六”。

### 5. 三类场景完整排名

| 场景 | 第1 | 第2 | 第3 | 第4 | 第5 |
|---|---|---|---|---|---|
| 科研长文本 | Kimi K3（0.6546699731） | Claude Fable 5（0.6470796358） | GPT-5.6 Sol（0.5703279480） | GPT-5.5（0.5275665754） | Claude Opus 4.8（0.3147246059） |
| 大众日常对话 | Claude Fable 5（0.7208273991） | Kimi K3（0.6342725548） | GPT-5.6 Sol（0.6023779374） | GPT-5.5（0.4391658605） | Claude Opus 4.8（0.3430603163） |
| 代码开发 | Claude Fable 5（0.7722288122） | Kimi K3（0.6840234806） | GPT-5.6 Sol（0.5838464654） | GPT-5.5（0.4896190898） | Claude Opus 4.8（0.3383686625） |

场景权重是根据题意和应用需求设定的偏好权重，与 CRITIC 权重各按 50% 组合；不是专家调查或 AHP 问卷。

### 6. 性能—成本

- 标准 workload：100 万输入 token + 20 万输出 token。
- 货币成本单位：USD / 标准 workload。

| 模型 | 成本（USD） | 通用性能 | Pareto |
|---|---:|---:|---|
| Kimi K3 | 6.0000 | 0.5933487598 | 是 |
| GPT-5.6 Sol | 11.0000 | 0.5177743845 | 否 |
| Claude Fable 5 | 16.0000 | 0.7253547227 | 是 |
| Claude Opus 4.8 | 10.0000 | 0.3901637084 | 否 |
| GPT-5.5 | 6.0000 | 0.4409692387 | 否 |
| GLM-5.2 | 1.9180 | NA | 不参与（缺少主排名性能） |

- Pareto front：Kimi K3、Claude Fable 5。
- 预算 `$6/$10/$12`：推荐 Kimi K3。
- 预算 `$16`：推荐 Claude Fable 5。
- 结论只适用于上述 workload 和截面标准价，不含缓存、Batch、区域加价、长上下文阶梯价或峰谷价格。

### 7. 严格效率比较范围

- 严格 compatible：Kimi K3、GPT-5.6 Sol、Claude Opus 4.8、GPT-5.5。
- Claude Fable 5：Opus fallback，`compatible=false`，只作补充记录。
- GLM-5.2：第三方 Together AI 部署且精度/量化未充分披露，`compatible=false`，只作补充记录。
- 严格效率指标来自 Artificial Analysis 约 10k input tokens、single prompt、标准化 500-token E2E、滚动 72 小时 P50；它们代表检索时段，不是永久属性。

### 8. 稳健性与回归

- 熵权法完整模型排名与 CRITIC 完全一致。
- 9 个权重分别乘 `0.8/0.9/1.1/1.2`，重新归一化，共 36 个扰动。
- 最低 Kendall tau：`0.8`。
- 前三名在全部扰动中保持 Fable、Kimi、GPT-5.6 Sol。
- 唯一换位：`HLE-Full × 1.2` 时 Claude Opus 4.8 与 GPT-5.5 互换第 4/5 名。
- 成本—性能对数回归：`n=5`，`R²=0.2241805179`，只允许称为当前样本内探索性关系。

## 二、论文禁止写错

- 禁止写“6 个模型均有统一可比效率数据”；应写“6 个 final 中仅 4 个具备严格可比效率数据”。
- 禁止写“场景权重来自专家调查”；应写“题意与应用需求驱动的场景偏好设定”。
- 禁止把小样本高相关写成统计证明；应写“样本内呈现较高秩相关，仅作为冗余判断的辅助证据”。
- 禁止写“所有数据均来自独立第三方”；能力数据主要来自官方技术报告的统一对照表，并辅以独立第三方来源。
- 禁止把成本—性能回归写成普遍规律或因果关系。
- 禁止使用 `compatible=false` 的 Fable/GLM 效率记录比较其效率高低。
- 禁止写“为了达到 75% 覆盖率而剔除三个模型”。
- 禁止将 GLM-5.2 写成主排名第 6。

## 三、LaTeX 填充映射

| 模板章节 | 唯一结果来源 | 应填内容 | 图表 | 主要警告 |
|---|---|---|---|---|
| 模型样本选择 | `data/model_candidates.csv`、`MODEL_SELECTION.md` | 9/6/3、exact version、excluded 理由 | 候选模型表 | 75% 不是唯一筛选目的 |
| 数据来源与预处理 | `data/processed/indicator_quality.csv`、`core_benchmark_matrix.csv` | 九指标、6/6 与 5/6、GLM 缺失 | 指标覆盖表 | 不插补；来源集中 |
| 问题一 CRITIC | `results/phase4/critic_weights.csv` | 九个权重 | `figures/critic_weights.svg` | n=5–6；Pearson 为逐对完整样本 |
| 问题一 TOPSIS | `results/phase4/general_ranking.csv` | 五模型得分与排名，GLM 未排名 | `figures/general_ranking.svg` | 模板距离公式必须与加权矩阵实现一致 |
| 问题二三场景 | `results/phase5/scenario_weights.csv`、`scenario_rankings.csv` | 三组完整排名与得分 | `figures/scenario_rank_changes.svg` | 场景偏好，不是专家调查 |
| 问题三成本/Pareto | `results/phase6/performance_cost.csv` | workload、成本、Pareto | `figures/performance_cost_pareto.svg` | 特定截面价；GLM 无性能分 |
| 问题三预算 | `results/phase6/budget_recommendations.csv` | `$6/$10/$12/$16` 推荐 | 预算推荐表 | 预算是 USD，不是无量纲指数 |
| 工程效率子分析 | `results/phase6/engineering_efficiency.csv` | 4 个 compatible 模型及部署分数 | 单独表格 | Fable/GLM 不得排名 |
| 稳健性 | `results/phase7/method_comparison.csv`、`rank_correlation.csv`、`rank_stability.csv` | 熵权一致、36 次、tau=0.8、唯一换位 | 稳健性表/图 | 仅局部单因素扰动 |
| 成本—性能回归 | `results/phase7/cost_performance_regression.csv` | n=5、方程、R² | 回归结果表 | 探索性，不外推、不因果 |

## 四、最终提交检查项

- [ ] 6 个 final 模型完全一致
- [ ] 3 个 excluded 模型理由一致
- [ ] 9 个核心指标完全一致
- [ ] CRITIC 权重与 CSV 一致
- [ ] TOPSIS 得分与 CSV 一致
- [ ] GLM 未误入主排名
- [ ] 三场景完整排名一致
- [ ] Pareto 前沿一致
- [ ] 四档预算推荐一致
- [ ] 效率只声明 4 个严格可比模型
- [ ] Fable/GLM 未被用于严格效率高低比较
- [ ] Artificial Analysis 滚动 72 小时 P50 已明确说明
- [ ] 36 次扰动结果一致
- [ ] Kendall tau 最低值一致
- [ ] 唯一第 4/5 名换位情形一致
- [ ] 回归写明 n=5 和 R²=0.2241805179
- [ ] 小样本限制已写
- [ ] Benchmark 厂商报告来源集中限制已写
- [ ] 临近截止日发布导致覆盖差异已写
- [ ] 场景权重未称为专家调查
- [ ] 价格适用 workload 与截面范围已写
- [ ] TOPSIS 公式与实际加权矩阵实现一致
- [ ] 没有使用截止日后的数据
- [ ] 没有学校、姓名、学号等匿名泄露
- [ ] 没有“待填写/待补写/待确定/todofigure”等占位内容进入终稿
- [ ] 图表数值、表题、正文结论三者一致
- [ ] 参考文献与来源 URL 已按竞赛格式整理
