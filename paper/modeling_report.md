# 主流大语言模型综合性能评价与选型研究

## 摘要

本文针对公开资料条件下的大语言模型综合评价问题，建立“数据冻结—口径清洗—指标筛选—客观赋权—场景评价—成本效益—稳健性检验”的完整流程。以 2026 年 8 月 17 日为统一数据截面，从 9 个候选模型中确定 Kimi K3、GPT-5.6 Sol、Claude Fable 5、Claude Opus 4.8、GPT-5.5 与 GLM-5.2 为研究池，并冻结高难推理、长文本、代码、专业任务、多模态和文档理解等 9 项指标。研究不自行调用模型测试，也不填补未公开成绩。

首先用覆盖率、方差及 Pearson/Spearman 相关分析筛选指标，再采用 CRITIC 确定客观权重，以 TOPSIS 对 5 个完整样本排序。Claude Fable 5、Kimi K3、GPT-5.6 Sol 分列综合排名前三；GLM-5.2 仅有 4/9 项同口径成绩，因此只作局部对照。其次，将客观权重与透明的场景偏好各按 50% 组合，得到科研长文本、日常对话和代码开发排序：Kimi K3 在科研长文本场景第一，在另两类场景第二。最后，以 100 万输入 token 与 20 万输出 token 为标准负载，Kimi K3 与 Claude Fable 5 构成性能—API 成本 Pareto 前沿；在可兼容效率子样本中，Kimi 的部署综合分最高。现有公开数据不含同硬件、同精度、同批量条件下的焦耳/token 或千瓦时指标，故本文不虚构计算能耗，而将 API 成本作为直接落地成本、将 TTFT/吞吐/总延迟作为兼容范围内的工程效率证据。熵权法与 36 组权重扰动表明主要结论总体稳健。

**关键词：** 大语言模型；CRITIC；TOPSIS；场景评价；Pareto 前沿；敏感性分析

## 1 问题重述与研究框架

题目要求解决三类问题：一是从公开且可核验的 Benchmark 中建立完整指标体系、筛选关键指标、合理赋权并评价主流模型，重点分析 Kimi K3；二是针对科研长文本、日常通用对话和代码开发建立场景化排序并解释差异；三是综合性能、使用成本与计算消耗，分析性能—落地成本效益并给出预算约束下的选择。

技术路线为：公开数据审计 → 固定可比 cohort → 缺失与单位检查 → 相关性和覆盖率筛选 → CRITIC 客观赋权 → TOPSIS 综合排序 → 场景偏好组合赋权 → 成本效益与 Pareto 分析 → 熵权法和权重扰动检验。

## 2 数据、假设与符号

### 2.1 数据边界与来源

统一截面为 2026-08-17。Benchmark 原始表含 148 条记录，模型元数据表含 9 条模型记录及 79 条逐字段证据，效率表含 9 条模型记录及 27 条逐指标证据。核心来源及其用途如下。

| 来源类型 | 主要来源 | 用途 |
|---|---|---|
| 同平台横向评测 | Artificial Analysis 模型页与榜单 | 固定版本、推理配置和效率口径 |
| 厂商官方资料 | Kimi、OpenAI、Anthropic、Z.ai 官方模型/定价页 | 模型版本、API 价格、上下文与能力说明 |
| Benchmark 官方资料 | HLE、Agents Last Exam 等官方榜单/论文 | 核验指标定义和原始成绩 |
| 仓库证据索引 | `data/sources/*.csv` | 保存 URL、检索日期、口径和字段级出处 |

最终研究池含 6 个模型。Gemini 3.1 Pro Preview 因 preview 状态及严格可比覆盖不足排除；DeepSeek V4 Pro 0813、Qwen3.8 2.4T A95B 距截止日仅 4 天和 5 天且分项数据不足，保留原始记录但不进入正式模型池。来源 URL 在第 11 节列出，逐字段证据以仓库索引为准。

### 2.2 基本假设

1. 固定来源 cohort 内的成绩可横向比较，但不同厂商的最高 reasoning effort 不代表相同计算预算。
2. 公布成绩只在本数据截面有效；滚动效率数据只代表检索窗口。
3. 9 项能力指标均为效益型指标，数值越大表示该项能力越强。
4. 缺失值不等于零。GLM-5.2 在冻结 cohort 中缺少 5 项核心成绩，均不插补，也不进入要求完整矩阵的 TOPSIS 主排名。

设模型为 \(i=1,\ldots,m\)，指标为 \(j=1,\ldots,n\)，原始值为 \(x_{ij}\)，标准化值为 \(z_{ij}\)，指标权重为 \(w_j\)。

## 3 数据清洗与指标筛选

所有核心记录均固定 benchmark 版本、测试设置及来源，形成 6×9 宽表和 54 行长表。百分制和 Elo 不直接求和，而是在建模阶段逐指标极差标准化：

\[
z_{ij}=\frac{x_{ij}-\min_i x_{ij}}{\max_i x_{ij}-\min_i x_{ij}}.
\]

候选指标先满足覆盖率不低于 80%、有效样本标准差非零，再检查相关性。9 项指标覆盖率均为 83.3% 或 100%。Spearman 绝对值不低于 0.9 的组合有两对：GPQA Diamond—MMMU-Pro（0.9211）与 SciCode—CharXiv RQ（0.9747）。但共同观测仅 5 个，且分别刻画文本科学推理与多模态推理、科学编程与研究文档理解，机械删除会损失题目所需的场景语义，因此保留全部 9 项，并将相关性风险纳入稳健性分析。

![Pearson 相关系数矩阵](../results/q1/pearson_heatmap.png)

## 4 CRITIC—TOPSIS 综合评价

### 4.1 CRITIC 权重

CRITIC 同时利用指标的对比强度和冲突性。令标准化指标 \(j\) 的标准差为 \(\sigma_j\)，指标间 Pearson 相关系数为 \(r_{jk}\)，则

\[
C_j=\sigma_j\sum_{k=1}^{n}(1-r_{jk}),\qquad w_j=\frac{C_j}{\sum_j C_j}.
\]

权重最高的三项为 HLE-Full（0.2013）、OmniDocBench（0.1483）和 AA-LCR（0.1270），最低为 SciCode（0.0674）。这些权重反映当前样本中的差异性与冲突性，不代表永久的重要性判断。

![CRITIC 指标权重](../results/q1/critic_weights_bar.png)

### 4.2 TOPSIS 排名与 GLM 局部对照

构造加权矩阵 \(v_{ij}=w_jz_{ij}\)，正、负理想解为各列最大值和最小值。模型到理想解的欧氏距离为 \(D_i^+\)、\(D_i^-\)，贴近度为

\[
S_i=\frac{D_i^-}{D_i^++D_i^-}.
\]

主排名只使用 9 项成绩完整的 5 个模型：

| 排名 | 模型 | TOPSIS 得分 |
|---:|---|---:|
| 1 | Claude Fable 5 | 0.7254 |
| 2 | Kimi K3 | 0.5933 |
| 3 | GPT-5.6 Sol | 0.5178 |
| 4 | GPT-5.5 | 0.4410 |
| 5 | Claude Opus 4.8 | 0.3902 |

![综合排名](../results/q1/topsis_ranking_bar.png)

GLM-5.2 的同口径局部成绩不参与总体赋权和排名，但可逐项定位：

| 同口径指标 | GLM-5.2 | 6 模型局部名次 | 局部领先者 | 与领先者差值 |
|---|---:|---:|---|---:|
| GPQA Diamond | 91.2 | 5 | GPT-5.6 Sol | 2.9 |
| AA-LCR | 71.3 | 4 | Kimi K3 | 3.4 |
| SciCode | 50.5 | 6 | Claude Fable 5 | 9.7 |
| GDPval-AA v2 | 1510 | 5 | Claude Fable 5 | 237 |

Z.ai 官方另报 HLE 40.5（with tools 为 54.7），但来源与测试 cohort 不同，只作为补充证据，不替换冻结矩阵中的 NA。四项视觉指标对纯文本 GLM-5.2 不适用。该做法避免把“未评价”误写成“低性能”。

![GLM-5.2 同口径局部对照](../results/phase4b/glm_partial_comparison.png)

### 4.3 Kimi K3 优势与短板

Kimi K3 在 AA-LCR 和 OmniDocBench 排名第一，在 SciCode、MMMU-Pro、CharXiv RQ 排名第二，体现出长文本推理、文档理解和科研材料处理优势。其 HLE-Full 标准化得分仅 0.1765，在 5 个完整模型中第 4，是最明确的短板；GPQA Diamond 与 GDPval-AA v2 位于中游。因此 Kimi 的竞争力集中于长文本和文档场景，而极高难度开放推理仍有提升空间。

![Kimi K3 分项雷达图](../results/q1/kimi_k3_radar.png)

## 5 三类场景评价

为体现应用偏好，本文为每个场景给出总和为 1 的主观优先权重 \(a_{sj}\)，再与 CRITIC 权重等比例组合：

\[
w_{sj}^{*}=0.5w_j+0.5a_{sj}.
\]

科研场景的前三项组合权重为 AA-LCR 0.1885、HLE-Full 0.1607、OmniDocBench 0.1341；日常对话为 HLE-Full 0.1607、GDPval-AA v2 0.1584、OmniDocBench 0.1241；代码开发为 SciCode 0.2337、HLE-Full 0.1407、GDPval-AA v2 0.1184。由此得到完整场景得分：

| 模型 | 科研长文本 | 日常对话 | 代码开发 |
|---|---:|---:|---:|
| Claude Fable 5 | 0.6471（2） | 0.7208（1） | 0.7722（1） |
| Kimi K3 | 0.6547（1） | 0.6343（2） | 0.6840（2） |
| GPT-5.6 Sol | 0.5703（3） | 0.6024（3） | 0.5838（3） |
| GPT-5.5 | 0.5276（4） | 0.4392（4） | 0.4896（4） |
| Claude Opus 4.8 | 0.3147（5） | 0.3431（5） | 0.3384（5） |

![三类场景得分与排名](../results/q2/scenario_rank_comparison.png)

Kimi 在科研长文本场景由综合第 2 升至第 1，机制是其 AA-LCR、OmniDocBench 优势在该场景被放大；在日常与代码场景仍为第 2。对每个指标权重分别乘 0.8、0.9、1.1、1.2 并归一化，共形成每场景 36 组扰动：Kimi 的科研名次为 1—2，保持第一的概率为 88.89%，最小 Kendall \(\tau=0.8\)；日常与代码名次始终为 2，\(\tau=1\)。

![Kimi K3 场景表现](../results/q2/kimi_k3_scenario_radar.png)

## 6 性能—成本与工程效率

### 6.1 标准负载与 Pareto 前沿

定义标准工作负载为 100 万输入 token 与 20 万输出 token，使用标准 API 单价：

\[
Cost_i=P_{in,i}+0.2P_{out,i}.
\]

| 模型 | 标准负载成本/美元 | 综合得分 | 性能/美元 | Pareto 前沿 |
|---|---:|---:|---:|:---:|
| Kimi K3 | 6 | 0.5933 | 0.0989 | 是 |
| GPT-5.5 | 6 | 0.4410 | 0.0735 | 否 |
| Claude Opus 4.8 | 10 | 0.3902 | 0.0390 | 否 |
| GPT-5.6 Sol | 11 | 0.5178 | 0.0471 | 否 |
| Claude Fable 5 | 20 | 0.7254 | 0.0363 | 是 |

![性能—成本 Pareto 前沿](../results/q3/performance_cost_pareto.png)

Kimi K3 与 Claude Fable 5 构成 Pareto 前沿。预算为 6、10、12、16 美元时，“预算内综合得分最高”均推荐 Kimi K3；预算达到 20 美元时推荐 Claude Fable 5。GLM-5.2 标准负载成本为 1.918 美元，但因能力覆盖不足，不能进入该推荐规则。

### 6.2 工程效率与计算能耗边界

仅对配置兼容的 Kimi K3、GPT-5.6 Sol、Claude Opus 4.8、GPT-5.5 比较 TTFT、输出速度和总延迟。将成本型指标正向化后等权平均得到工程效率，再按 70% 综合性能与 30% 工程效率计算部署分：Kimi K3 为 0.5862（第 1），GPT-5.5 为 0.5582（第 2），Claude Opus 4.8 为 0.5010（第 3），GPT-5.6 Sol 为 0.4309（第 4）。Claude Fable 5 记录含 Opus fallback，GLM-5.2 为第三方部署，均不作硬比较。

![性能与工程效率组合](../results/q3/engineering_efficiency.png)

题目同时要求考虑计算消耗。经逐模型审计，当前公开数据均没有同硬件、同批量、同精度和同输出长度下的功率、焦耳/token 或 kWh 记录，因此 `energy_data_available=False`。参数量不能代替推理时激活参数，延迟和吞吐也不能代替功率，本文不据此估算能耗。当前可回答的是直接 API 落地成本和兼容配置下的时间效率；若后续获得统一测试，应记录 GPU 型号与数量、量化精度、batch、输入/输出长度、平均功率和总时间，并以 J/token 或 kWh/任务加入成本函数。

## 7 稳健性与规律分析

熵权法得到的完整模型排名与 CRITIC 完全一致。对 9 个 CRITIC 权重分别进行 ±10%、±20% 单因素扰动，共 36 组；Claude Fable 5、Kimi K3、GPT-5.6 Sol 始终保持第 1、2、3，GPT-5.5 与 Claude Opus 4.8 仅出现一次相邻换位，最小 Kendall \(\tau=0.8\)。场景权重的独立扰动结果见第 5 节。

对 5 个完整模型拟合探索性关系

\[
Performance=0.1994+0.1481\ln(Cost),
\]

得到 \(R^2=0.3147\)、调整 \(R^2=0.0862\)、RMSE=0.0978。样本仅为 5，故只能描述“价格与性能存在弱正相关、价格解释力有限”，不能作因果推断。

## 8 模型评价与局限

本方法的优点是来源可追溯、比较 cohort 固定、缺失处理保守、权重与排序可复现，并通过场景、成本和稳健性形成闭环。主要局限如下：

1. 最终研究池仅 6 个模型，主排名完整样本为 5 个，相关系数与回归不宜外推。
2. 核心横向表虽设置一致，但仍可能存在厂商报告偏差；滚动平台数据也只代表截面。
3. GLM-5.2 仅有 4 项同口径能力数据，当前不能给出公平总排名。
4. 效率子样本只有 4 个兼容配置，且无法覆盖 Claude Fable 5 和 GLM-5.2。
5. 价格未纳入区域、缓存命中、batch、长上下文阶梯或峰谷套餐，预算结论只对应本文标准负载。
6. 同口径计算能耗数据完全缺失，当前不能报告能耗排名或把能耗折算为货币成本。
7. 场景主观权重虽透明，仍应在专家问卷或团队评审后更新。

## 9 结论

在不插补缺失数据的前提下，Claude Fable 5 获得通用综合评价第一，Kimi K3 第二。Kimi 的核心优势是长文本、文档理解和科研材料处理，其主要短板是 HLE-Full 所代表的极高难度开放推理；在科研长文本场景中升至第一。标准 API 负载下，Kimi 与 Claude Fable 5 构成 Pareto 前沿，Kimi 在中低预算区间和兼容工程效率子样本中具有更好的落地平衡。主排名与绝大多数场景结论经替代赋权和扰动检验后稳定。所有结论均限定在本数据截面、固定 cohort、完整样本和已声明的成本口径内。

## 10 复现说明

在仓库根目录安装 `requirements.txt` 后运行：

```bash
python scripts/run_pipeline.py
python scripts/run_q1.py
python scripts/run_glm_supplement.py
python scripts/run_q2.py
python scripts/run_q3.py
python scripts/validate_q1.py
python scripts/validate_q2_q3.py
python -m unittest discover tests -v
python scripts/build_paper.py
python scripts/validate_paper.py
```

原始题面保存在 `references/problem/TJMML_B.pdf`，逐项符合性矩阵在 `docs/problem_compliance_matrix.md`；中间结果分别位于 `results/phase3/` 至 `results/phase7/` 以及 `results/q1/` 至 `results/q3/`。

## 11 数据来源与可追溯性

- Kimi K3 官方介绍：<https://www.kimi.com/blog/kimi-k3>
- Kimi API 说明：<https://www.kimi.com/help/kimi-api/api-troubleshooting>
- OpenAI 模型文档：<https://developers.openai.com/api/docs/models/gpt-5.6-sol>
- OpenAI API 定价：<https://platform.openai.com/docs/pricing/>
- Anthropic 模型与定价：<https://platform.claude.com/docs/en/about-claude/pricing>
- Z.ai GLM-5.2 文档：<https://docs.bigmodel.cn/cn/guide/models/text/glm-5.2>
- Z.ai API 定价：<https://open.bigmodel.cn/pricing>
- GLM-5.2 官方模型卡：<https://huggingface.co/zai-org/GLM-5.2>
- Artificial Analysis：<https://artificialanalysis.ai/>

以上列表提供可阅读入口；用于计算的每一个有效字段仍以 `data/sources/benchmark_sources.csv`、`metadata_sources.csv`、`efficiency_sources.csv` 中记录的精确 URL、检索日期和口径说明为准。
