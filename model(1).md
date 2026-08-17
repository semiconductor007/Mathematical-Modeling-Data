# B 题：主流大语言模型综合性能评价建模 — 建模方案

> **文档用途**：建模手与代码手交接，明确每个问题的建模方法、公式、步骤与图表要求。
>
> **数据仓库**：<https://github.com/semiconductor007/Mathematical-Modeling-Data>
>
> **数据截面**：`DATA_CUTOFF_DATE = 2026-08-17`
>
> **约定**：本文档只写"怎么建、怎么算、画什么图"，**不写具体结果数值**。所有结果表由代码手运行脚本后生成、建模手填写进论文；图表位置标注中给出图名、图类型（2D/3D）、绘制内容与数据来源。

---

## 0 数据概览与充分性评估

### 0.1 数据来源审计结论

仓库数据**充分且来源可追溯**，满足赛题"数据来源应为各模型官方白皮书、AI 评测权威平台公开基准、行业通用标准化测试集结果"的要求。

| 数据类别         | 文件路径                            | 记录数   | 来源覆盖                                                                        | 充分性   |
| ------------ | ------------------------------- | ----- | --------------------------------------------------------------------------- | ----- |
| Benchmark 能力 | `data/raw/benchmark_scores.csv` | 148 条 | Kimi K3 官方技术报告、OpenAI 发布报告、Artificial Analysis、Z.ai 官方、Agents' Last Exam 榜单 | ✅ 充分  |
| 模型元数据与价格     | `data/raw/model_metadata.csv`   | 9 个模型 | 各厂商官方 API 文档/模型卡/定价页                                                        | ✅ 充分  |
| 推理效率         | `data/raw/cost_efficiency.csv`  | 9 个模型 | Artificial Analysis API Provider Performance Benchmarking                   | ✅ 充分  |
| 来源索引         | `data/sources/*.csv`            | 3 张表  | 逐字段登记 source_url、retrieval_date、reliability_level                           | ✅ 可追溯 |

**来源分级**（DATA_RULES.md 定义）：

- **Level A**：同一权威独立第三方平台横向评测（Artificial Analysis Intelligence Index v4.1.1）
- **Level B**：Benchmark 官方榜单（Agents' Last Exam leaderboard）
- **Level C**：厂商官方技术报告/模型卡/API 文档（Kimi K3 官方报告、OpenAI 发布报告、Anthropic 官方、Z.ai 官方）
- **Level D**：可靠但非一手资料（仅辅助，不进入核心模型）

### 0.2 最终模型池

| model_id        | 厂商          | 模型              | 发布日期       | Benchmark 覆盖      | 状态                       |
| --------------- | ----------- | --------------- | ---------- | ----------------- | ------------------------ |
| kimi-k3         | Moonshot AI | Kimi K3         | 2026-07-16 | 17/24 raw (70.8%) | **final**（题目指定必选）        |
| gpt-5.6-sol     | OpenAI      | GPT-5.6 Sol     | 2026-07-09 | 23/24 raw (95.8%) | **final**                |
| claude-fable-5  | Anthropic   | Claude Fable 5  | 2026-06-09 | 21/24 raw (87.5%) | **final**                |
| claude-opus-4.8 | Anthropic   | Claude Opus 4.8 | 2026-05-28 | 23/24 raw (95.8%) | **final**                |
| gpt-5.5         | OpenAI      | GPT-5.5         | 2026-04-23 | 23/24 raw (95.8%) | **final**                |
| glm-5.2         | Z.ai        | GLM-5.2         | 2026-06-16 | 10/24 raw (41.7%) | **final**（国产开源代表，独立简要分析） |

> 排除模型：Gemini 3.1 Pro Preview（preview 状态 + 严格可比覆盖不足）、DeepSeek V4 Pro 0813（距截止日仅 4 天）、Qwen3.8 2.4T A95B（距截止日仅 5 天）。原始数据保留但不进入正式建模。

### 0.3 核心指标体系（9 项）

| 指标                    | 维度     | 覆盖率         | 数据来源 cohort                      |
| --------------------- | ------ | ----------- | -------------------------------- |
| GPQA Diamond          | 高难度推理  | 100% (6/6)  | Kimi K3 官方报告对照表                  |
| HLE-Full (no tools)   | 高难度推理  | 83.3% (5/6) | Kimi K3 官方报告对照表                  |
| AA-LCR                | 长文本理解  | 100% (6/6)  | Artificial Intelligence Index 快照 |
| SciCode               | 代码能力   | 100% (6/6)  | Artificial Intelligence Index 快照 |
| GDPval-AA v2          | 专业任务   | 100% (6/6)  | Artificial Intelligence Index 快照 |
| MMMU-Pro (no tools)   | 多模态    | 83.3% (5/6) | Kimi K3 官方报告对照表                  |
| OmniDocBench          | 文档理解   | 83.3% (5/6) | Kimi K3 官方报告对照表                  |
| CharXiv RQ (no tools) | 研究文档推理 | 83.3% (5/6) | Kimi K3 官方报告对照表                  |
| MathVision (no tools) | 多模态数学  | 83.3% (5/6) | Kimi K3 官方报告对照表                  |

> **GLM-5.2 数据缺口**：主 cohort 中仅有 4/9 项核心成绩（GPQA、AA-LCR、SciCode、GDPval）；HLE-Full 未报告（独立 Z.ai cohort 官方值 40.5 保留，不跨口径替换）；4 项视觉指标（MMMU-Pro、OmniDocBench、CharXiv RQ、MathVision）因纯文本模型结构性不适用。**因此 GLM-5.2 不参与要求完整矩阵的 TOPSIS 主排名，在 §2.6 做单独简要分析。**

### 0.4 核心数据矩阵（6×9）

数据文件：`data/processed/core_benchmark_matrix.csv`

| model_id        | GPQA | HLE  | AA-LCR | SciCode | GDPval | MMMU-Pro | OmniDoc | CharXiv | MathVision |
| --------------- | ---- | ---- | ------ | ------- | ------ | -------- | ------- | ------- | ---------- |
| kimi-k3         | 93.5 | 43.5 | 74.7   | 58.7    | 1686   | 81.6     | 91.1    | 84.8    | 94.3       |
| gpt-5.6-sol     | 94.1 | 44.5 | 73.7   | 56.1    | 1736   | 83.0     | 85.8    | 84.6    | 95.8       |
| claude-fable-5  | 92.6 | 53.3 | 70.0   | 60.2    | 1747   | 81.2     | 89.8    | 88.9    | 94.8       |
| claude-opus-4.8 | 91.0 | 49.8 | 67.7   | 53.5    | 1593   | 78.9     | 87.9    | 80.5    | 86.7       |
| gpt-5.5         | 93.5 | 41.4 | 74.3   | 56.1    | 1491   | 81.2     | 89.4    | 84.1    | 92.2       |
| glm-5.2         | 91.2 | NA   | 71.3   | 50.5    | 1510   | NA       | NA      | NA      | NA         |

> 单位：GPQA–MathVision 为 percent；GDPval-AA v2 为 Elo（human baseline=1000）。所有指标均为效益型（越大越好）。本表为**输入数据**，非建模结果。

---

## 1 总体技术路线

```
公开数据审计 → 固定可比 cohort → 缺失与单位检查 → 相关性分析与指标筛选
    → CRITIC 客观赋权 → TOPSIS 综合排序（问题1，GLM-5.2 单独分析）
    → 场景偏好组合赋权 → 三类场景排名（问题2）
    → 成本效益模型 → Pareto 前沿 → 预算选型策略（问题3）
    → 熵权法 + 权重扰动 → 稳健性检验
```

> **📊 图表位置【图1｜2D 流程图】**：**技术路线流程图**。绘制内容：方框+箭头串联从数据收集到稳健性检验的完整流程，每个方框标注阶段名与主要输出物（如"CRITIC 赋权 → 权重向量 $w_j$"、"TOPSIS → 综合得分 $S_i$"）。绘制要求：横向主流程 + 纵向数据/结果支线，配色区分"数据处理/建模/输出"三类节点。

---

## 2 问题一：指标体系构建与综合评价

### 2.1 指标梳理与筛选

#### 2.1.1 候选指标池

从赛题提示的维度出发，梳理大模型性能评价潜在指标：

| 能力维度     | 候选 Benchmark                                                 | 选取理由        |
| -------- | ------------------------------------------------------------ | ----------- |
| 高难度推理    | GPQA Diamond, HLE-Full, FrontierMath                         | 科学/开放推理能力锚点 |
| 长文本理解    | AA-LCR, GraphWalks                                           | 长上下文检索与推理   |
| 代码能力     | SciCode, SWE-Bench Pro, Terminal-Bench, DeepSWE, FrontierSWE | 科学编程与软件工程   |
| 专业任务     | GDPval-AA v2, OfficeQA Pro                                   | 真实经济价值任务    |
| 多模态      | MMMU-Pro, MathVision                                         | 图文多模态推理     |
| 文档理解     | OmniDocBench, CharXiv RQ                                     | 文档感知与研究图表推理 |
| Agent 能力 | Agents' Last Exam                                            | 复杂 agent 任务 |

#### 2.1.2 筛选准则

对每个候选指标 $j$，计算覆盖率：

$\text{Coverage}_j = \frac{\text{该指标有效数据模型数}}{\text{最终模型总数}(m=6)}$

**筛选规则**：

1. $\text{Coverage}_j \geq 75\%$（6 个模型中至少 5 个有数据）
2. 变异系数 $CV_j = \sigma_j / \mu_j \neq 0$（指标有区分度）
3. `compatible=true`：测试设置（版本、工具策略、推理强度、采样参数）在 cohort 内一致
4. 保留不同语义维度，避免单一维度重复

**预期输出**：从 17 个候选 Benchmark 中冻结 9 个核心指标（预期结果为 §0.3 所列，最终以代码手运行 `results/core_indicator_selection.csv` 为准）。

> 已知被排除指标及原因（数据事实）：Terminal-Bench/FrontierSWE/Agents' Last Exam/OfficeQA Pro 因 `compatible=false`（harness 因模型而异）；SWE-Bench Pro/DeepSWE 同理；FrontierMath/GraphWalks 因 Kimi K3 和 GLM-5.2 缺失导致覆盖率不足。

> **📊 图表位置【图2｜2D 结构图】**：**指标筛选漏斗图**（或指标体系树状图）。绘制内容：从上到下展示"候选池 17 项 → 覆盖率不足剔除 → compatible=false 剔除 → 维度去重 → 冻结 9 项"，每层标注剔除数量与原因。绘制要求：漏斗式梯形分层，每层右侧标注剩余指标数。

> **📊 图表位置【表1】**：核心指标选取表，列出指标名称、维度、版本、工具策略、覆盖率、选取理由（数据来源 `results/core_indicator_selection.csv`，由代码手生成）。

### 2.2 相关性分析

#### 2.2.1 方法

对 6×9 核心矩阵计算 **Pearson 线性相关系数** 和 **Spearman 秩相关系数**：

$r_{jk}^{\text{Pearson}} = \frac{\sum_{i=1}^{m}(x_{ij}-\bar{x}_j)(x_{ik}-\bar{x}_k)}{\sqrt{\sum_{i=1}^{m}(x_{ij}-\bar{x}_j)^2 \sum_{i=1}^{m}(x_{ik}-\bar{x}_k)^2}}$

$r_{jk}^{\text{Spearman}} = 1 - \frac{6\sum_{i=1}^{m}d_i^2}{m(m^2-1)}$

其中 $d_i$ 为模型 $i$ 在指标 $j$ 和 $k$ 上的秩差。

#### 2.2.2 分析步骤与判定规则

1. 计算 9×9 两两相关系数矩阵（含 NA 的列用 pairwise deletion，即仅用共同有效样本）
2. 标注共同样本数 $n_{jk}$；由于 $n_{jk}$ 仅 5–6，相关系数不稳定，需结合**语义维度**判断
3. **判定规则**：仅当"相关系数 $|r|>0.9$ **且** 两指标属于同一语义维度"时才考虑剔除；跨维度高相关对（如文本推理 vs 多模态推理）保留，作为稳健性风险标注
4. 决策记录写入 `results/phase3/redundancy_flags.csv`

> **📊 图表位置【图3｜2D 热力图】**：**Pearson 相关性热力图**（下三角矩阵，9×9）。绘制内容：每个格子填充颜色（蓝→白→红渐变，对应 -1→0→+1），格内标注相关系数值；$|r|>0.9$ 的高相关对用加粗红框圈出。绘制要求：行列标签为指标全名，对角线与上三角留白或置灰。

> **📊 图表位置【表2】**：高相关指标对审查表，列出指标对、Pearson、Spearman、共同样本数、维度是否相同、决策与理由（数据来源 `results/phase3/redundancy_flags.csv`）。

### 2.3 指标权重确定 — CRITIC 法

#### 2.3.1 方法选择论证

选择 **CRITIC（Criteria Importance Through Intercriteria Correlation）** 客观赋权法，理由：

- 同时利用指标的**对比强度**（标准差）和**冲突性**（指标间相关性），比熵权法信息量更丰富
- 纯数据驱动，避免主观偏好
- 结果可复现、可审计

#### 2.3.2 数据标准化

由于指标单位不同（percent vs Elo），先做极差标准化（min-max normalization）。所有指标均为效益型：

$z_{ij} = \frac{x_{ij} - \min_i x_{ij}}{\max_i x_{ij} - \min_i x_{ij}}$

> 对含 NA 的指标（HLE-Full、MMMU-Pro 等），仅对有值的模型计算 min/max，NA 保持 NA。

#### 2.3.3 CRITIC 权重计算

**步骤 1**：计算标准化后各指标的标准差（对比强度）：

$\sigma_j = \sqrt{\frac{1}{m_j - 1}\sum_{i \in I_j}(z_{ij} - \bar{z}_j)^2}$

其中 $m_j$ 为指标 $j$ 的有效模型数，$I_j$ 为有效模型集合。

**步骤 2**：计算指标 $j$ 的冲突性：

$F_j = \sum_{k=1}^{n}(1 - r_{jk})$

其中 $r_{jk}$ 为指标 $j$ 与 $k$ 的 Pearson 相关系数。$r_{jk}$ 越大，冲突性越小。

**步骤 3**：计算信息含量：

$C_j = \sigma_j \cdot F_j$

**步骤 4**：归一化得到权重：

$w_j = \frac{C_j}{\sum_{k=1}^{n} C_k}$

#### 2.3.4 输出物要求

运行后生成 `results/phase4/critic_weights.csv`，列结构如下（**数值由代码手运行后填写**）：

| 指标     | 标准差 $\sigma_j$ | 冲突性 $F_j$ | 信息含量 $C_j$ | 权重 $w_j$ |
| ------ | -------------- | --------- | ---------- | -------- |
| …（9 行） | 待填             | 待填        | 待填         | 待填       |

> 论文写作提示（供建模手判断）：通常 HLE-Full、AA-LCR、OmniDocBench 因区分度与独立性较强而权重偏高，具体以运行结果为准，并需解释高权重指标的统计含义（区分度大、与其他指标相关性低）。

> **📊 图表位置【图4｜2D 条形图】**：**CRITIC 指标权重条形图**。绘制内容：9 个指标按权重降序排列的水平条形图，条内/条端标注 $w_j$ 数值，最高权重条用强调色。数据来源 `results/phase4/critic_weights.csv`。

### 2.4 TOPSIS 综合评价

#### 2.4.1 方法

TOPSIS（逼近理想解排序法）通过计算各方案与正/负理想解的距离进行排序。

**步骤 1**：构造加权标准化矩阵：

$v_{ij} = w_j \cdot z_{ij}$

**步骤 2**：确定正理想解 $A^+$ 和负理想解 $A^-$：

$A^+ = \left(\max_i v_{i1},\ \max_i v_{i2},\ \ldots,\ \max_i v_{in}\right)$

$A^- = \left(\min_i v_{i1},\ \min_i v_{i2},\ \ldots,\ \min_i v_{in}\right)$

**步骤 3**：计算各模型到正/负理想解的欧氏距离：

$D_i^+ = \sqrt{\sum_{j=1}^{n}(v_{ij} - v_j^+)^2}$

$D_i^- = \sqrt{\sum_{j=1}^{n}(v_{ij} - v_j^-)^2}$

**步骤 4**：计算贴近度（综合得分）：

$S_i = \frac{D_i^-}{D_i^+ + D_i^-}$

$S_i \in [0, 1]$，越接近 1 表示越优。

**参与范围**：仅 9 项成绩完整的 5 个模型（kimi-k3、gpt-5.6-sol、claude-fable-5、claude-opus-4.8、gpt-5.5）参与主排名；GLM-5.2 标记 `not_ranked_insufficient_coverage`，不进入主排名（单独分析见 §2.6）。

#### 2.4.2 输出物要求

运行后生成 `results/phase4/general_ranking.csv`，列结构如下（**数值待填**）：

|                     排名 | 模型 | $D_i^+$ | $D_i^-$ | TOPSIS 得分 $S_i$ |
| ---------------------: | -- | ------- | ------- | --------------- |
| …（5 行 + GLM-5.2 标注不排名） | 待填 | 待填      | 待填      | 待填              |

> **📊 图表位置【图5｜2D 条形图】**：**TOPSIS 综合排名条形图**。绘制内容：5 个完整模型按得分降序排列的水平条形图，条端标注 $S_i$ 数值与排名序号，第 1 名用强调色。GLM-5.2 可放在图右下方以灰色"数据不足未参与排名"注释块标注，不进坐标轴。数据来源 `results/phase4/general_ranking.csv`。

> **📊 图表位置【表3】**：标准化得分明细表，列出每个模型在 9 个指标上的原始值和标准化值（数据来源 `results/phase4/normalized_scores.csv`）。

### 2.5 Kimi K3 优势与短板分析

#### 2.5.1 分析步骤

1. 取 Kimi K3 在 9 个核心指标上的标准化得分 $z_{\text{kimi},j}$ 及对应位次
2. 按位次分档：位次 1 = **优势**、位次 2 = **次优势**、位次 ≥3 = **中游/短板**（其中显著落后于第 1 名且位次靠后的标记为**短板**）
3. 对每项指标计算与第 1 名的标准化差距 $\Delta_j = z_{\max,j} - z_{\text{kimi},j}$
4. 汇总输出 `results/phase4/kimi_strengths_weaknesses.csv`

#### 2.5.2 输出物要求

| 指标     | Kimi 标准化得分 | 排名 | 领先模型 | 与领先差距 | 评估 |
| ------ | ---------- | -- | ---- | ----- | -- |
| …（9 行） | 待填         | 待填 | 待填   | 待填    | 待填 |

> 论文写作提示：优势部分通常集中在长文本理解（AA-LCR）、文档理解（OmniDocBench）等 Kimi 官方报告强调的维度；短板部分关注 HLE-Full 等极高难度开放推理。以运行结果为准，结论需逐项对应数据，不得空泛。

> **📊 图表位置【图6｜2D 雷达图】**：**Kimi K3 能力雷达图**。绘制内容：9 个指标标准化得分构成的闭合多边形，可与排名第 1 的模型（或全体均值）叠加对比；优势轴区域填充强调色、短板轴用虚线/警示色标注。绘制要求：9 轴均匀分布，轴标签用指标简称，比例尺统一为 [0,1]。数据来源 `results/phase4/normalized_scores.csv`。

### 2.6 GLM-5.2 单独简要分析（数据不完整模型的补充评价）

> **定位**：GLM-5.2 在主 cohort 中仅 4/9 项成绩，不满足 TOPSIS 主排名条件，但作为国产开源代表模型（赛题重点考察对象之一），**必须给出有数据支撑的简要评价**，避免论文出现"该模型完全未被分析"的漏洞。本节采用"局部可比 + 官方数据参照 + 结构性说明"的三层分析框架。

#### 2.6.1 可得数据盘点

| 数据项          | 值    | 口径                 | 可比性             |
| ------------ | ---- | ------------------ | --------------- |
| GPQA Diamond | 91.2 | 主 cohort（AA 快照）    | ✅ 与 5 个完整模型直接可比 |
| AA-LCR       | 71.3 | 主 cohort（AA 快照）    | ✅ 直接可比          |
| SciCode      | 50.5 | 主 cohort（AA 快照）    | ✅ 直接可比          |
| GDPval-AA v2 | 1510 | 主 cohort（AA 快照）    | ✅ 直接可比          |
| HLE 官方       | 40.5 | Z.ai 官方 cohort（独立） | ⚠️ 仅定性参照，不跨口径替换 |
| 4 项视觉指标      | —    | 纯文本模型，结构性不适用       | ❌ 不适用           |

#### 2.6.2 分析步骤

1. **局部位次对比**：将 GLM-5.2 的 4 项可得成绩分别插入 5 个完整模型中，计算其在 6 个模型中的位次与相对差距（$\Delta_j = \max_k x_{kj} - x_{\text{glm},j}$），得到"文本推理/长文本/代码/专业任务"四方面的定位结论
2. **官方数据参照**：引用 Z.ai 官方 HLE 40.5，与主 cohort 中 HLE 值（Kimi 43.5 等）做**口径说明下的定性比较**（明确声明 cohort 不同，仅观察数量级差异，不做精确排名）
3. **结构性缺失说明**：4 项视觉指标因纯文本模型不适用，属结构性限制而非性能短板，论文需明示
4. **性价比视角补充**：结合 GLM-5.2 标准工作负载成本（§4.1，约 $1.92），分析其"低价 + 中游文本能力"的定位，衔接问题三的成本效益框架
5. 结论写作框架：**定位为"高性价比国产开源模型"**，文本类能力处于中游、与头部旗舰存在可量化的差距、视觉多模态缺失是结构性天花板——每个结论必须引用第 1–4 步的数值依据

#### 2.6.3 输出物与图表要求

> **📊 图表位置【图7｜2D 分组条形图】**：**GLM-5.2 局部能力对比图**。绘制内容：4 项可得指标（GPQA、AA-LCR、SciCode、GDPval）各自绘制 6 个模型（含 GLM-5.2）的得分条，GLM-5.2 用强调色、其余用灰色，每项标注 GLM-5.2 位次。绘制要求：2×2 子图排布或 4 组并排；GDPval 需标注 Elo 单位与 human baseline 参考线。数据来源 `data/processed/core_benchmark_matrix.csv`。

> **📊 图表位置【图8｜2D 散点图（可选）】**：**GLM-5.2 官方 HLE 参照图**。绘制内容：主 cohort 5 个模型的 HLE-Full 得分散点/条形 + 独立标注 GLM-5.2 官方 HLE 40.5（用不同形状/颜色 + "Z.ai 官方口径"注释框），直观展示"口径不同仅参照"的处理方式。

> 注：图 7、图 8 为 GLM-5.2 专属图，纳入问题一的图表组。

### 2.7 问题一补充可视化（数据矩阵全景）

> **📊 图表位置【图9｜3D 柱状图】**：**指标 × 模型得分三维柱状图**。绘制内容：X 轴为 9 个指标、Y 轴为 6 个模型、Z 轴为标准化得分（[0,1]）；每个（指标, 模型）组合一根柱，GLM-5.2 的 5 个 NA 位置留空或用镂空柱占位。绘制要求：视角建议俯视 30°–45°，加图例区分"完整数据/缺失"，旋转视角展示数据矩阵的完整结构与缺失模式。数据来源 `data/processed/core_benchmark_matrix.csv`（标准化后）。

> 该图作用：一图展示完整数据矩阵、缺失结构（GLM-5.2）与指标间分布差异，作为问题一的开场数据可视化。

---

## 3 问题二：场景化评价模型

### 3.1 场景定义

根据赛题要求设定三类典型落地场景：

| 场景       | 核心需求              | 权重倾斜指标                             |
| -------- | ----------------- | ---------------------------------- |
| 科研长文本分析  | 长文档理解、研究图表推理、文档感知 | AA-LCR, CharXiv RQ, OmniDocBench   |
| 大众日常通用对话 | 通用推理、多模态、专业任务     | GDPval-AA v2, MMMU-Pro, MathVision |
| 计算机代码开发  | 科学编程、代码生成         | SciCode                            |

### 3.2 组合赋权模型

#### 3.2.1 方法

采用**客观—主观组合赋权法**，将 CRITIC 客观权重 $w_j$ 与场景主观偏好权重 $a_{sj}$ 线性组合：

$w_{sj}^* = \alpha \cdot w_j + (1-\alpha) \cdot a_{sj}$

其中：

- $w_j$：CRITIC 客观权重（问题一已确定）
- $a_{sj}$：场景 $s$ 下指标 $j$ 的主观权重，满足 $\sum_j a_{sj} = 1$
- $\alpha$：客观权重占比，取 $\alpha = 0.5$（保留一半客观信息，降低完全依赖主观赋权的风险）

> 组合后权重自动归一化（因 $w_j$ 和 $a_{sj}$ 均已归一化，线性组合权重和仍为 1）。论文中需论证 $\alpha=0.5$ 的合理性（主客观信息对半、避免任一极端）。

#### 3.2.2 场景主观权重设定（输入参数，代码手直接采用）

**科研长文本场景**（$s = \text{research}$）：

| 指标       | GPQA | HLE  | AA-LCR   | SciCode | GDPval | MMMU-Pro | OmniDoc | CharXiv  | MathVision |
| -------- | ---- | ---- | -------- | ------- | ------ | -------- | ------- | -------- | ---------- |
| $a_{sj}$ | 0.12 | 0.12 | **0.25** | 0.05    | 0.08   | 0.08     | 0.12    | **0.13** | 0.05       |

**日常通用对话场景**（$s = \text{daily}$）：

| 指标       | GPQA | HLE  | AA-LCR | SciCode | GDPval   | MMMU-Pro | OmniDoc | CharXiv | MathVision |
| -------- | ---- | ---- | ------ | ------- | -------- | -------- | ------- | ------- | ---------- |
| $a_{sj}$ | 0.12 | 0.12 | 0.10   | 0.03    | **0.20** | **0.15** | 0.10    | 0.06    | 0.12       |

**代码开发场景**（$s = \text{code}$）：

| 指标       | GPQA | HLE  | AA-LCR | SciCode  | GDPval | MMMU-Pro | OmniDoc | CharXiv | MathVision |
| -------- | ---- | ---- | ------ | -------- | ------ | -------- | ------- | ------- | ---------- |
| $a_{sj}$ | 0.12 | 0.08 | 0.08   | **0.40** | 0.12   | 0.05     | 0.05    | 0.05    | 0.05       |

> 设定依据：场景需求越强，主观权重越高；非核心指标保留 0.03–0.12 的基准权重避免零权重。论文需用一段话说明倾斜逻辑（例如科研场景将 AA-LCR 提至 0.25 因为长文档检索是该场景第一刚需）。

#### 3.2.3 组合权重计算

$w_{sj}^* = 0.5 \cdot w_j + 0.5 \cdot a_{sj}$

运行后生成 `results/phase5/scenario_weights.csv`（3 场景 × 9 指标，**数值待填**）。

### 3.3 场景化 TOPSIS 排序

用组合权重 $w_{sj}^*$ 替代通用权重 $w_j$，对 5 个完整模型重新执行 TOPSIS（步骤同 §2.4，公式 $v_{ij} = w_{sj}^* \cdot z_{ij}$），得到各场景排名。

**输出物要求**：运行后生成 `results/phase5/scenario_rankings.csv`，列结构如下（**数值待填**）：

| 场景    | 第 1 名 (得分) | 第 2 名 (得分) | 第 3 名 (得分) | 第 4 名 (得分) | 第 5 名 (得分) |
| ----- | ---------- | ---------- | ---------- | ---------- | ---------- |
| 科研长文本 | 待填         | 待填         | 待填         | 待填         | 待填         |
| 日常对话  | 待填         | 待填         | 待填         | 待填         | 待填         |
| 代码开发  | 待填         | 待填         | 待填         | 待填         | 待填         |

> **📊 图表位置【图10｜2D 斜率图/分组条形图】**：**场景排名变化对比图**。绘制内容：X 轴为三个场景、Y 轴为综合得分，每个模型一条折线（斜率图），或按场景分组的条形图；重点突出"某模型在某场景排名跃升/回落"的变化（预期关注 Kimi K3 在科研长文本场景的排名变化）。数据来源 `results/phase5/scenario_rankings.csv`。

> **📊 图表位置【图11｜2D 热力图】**：**场景组合权重热力图**。绘制内容：3 行（场景）× 9 列（指标），格内填组合权重 $w_{sj}^*$，颜色深浅对应权重大小，行内权重总和标注 1。数据来源 `results/phase5/scenario_weights.csv`。

### 3.4 差异机理分析（写作框架）

对"同一模型在不同场景排名变化"和"同一场景下模型间排名变化"给出机理解释，分析模板：

1. **权重变化追踪**：对比通用权重 $w_j$ 与场景组合权重 $w_{sj}^*$ 的增减（如某指标权重从 $w_j$ 升至 $w_{sj}^*$，则该场景向该指标倾斜）
2. **模型-指标匹配**：结合 §2.5 各模型强弱项，判断权重倾斜方向利好哪个模型（模型在权重提升指标上的标准化得分越高，获益越大）
3. **结论句式**："模型 A 在场景 s 排名上升，源于其领先指标（列表）在场景 s 中被赋予更高权重（$w_j \to w_{sj}^*$），拉大了与对手的加权差距"

> 论文需针对 3 个场景各写一段机理分析，全部引用场景权重与标准化得分数据，禁止无数据支撑的定性描述。

> **📊 图表位置【图12｜3D 柱状图】**：**场景 × 模型综合得分三维柱状图**。绘制内容：X 轴 3 场景、Y 轴 5 模型、Z 轴得分 $S_i$，柱顶标注数值；同一模型三根柱用同色系区分场景，便于观察"同一模型的跨场景起伏"。数据来源 `results/phase5/scenario_rankings.csv`。

---

## 4 问题三：性能—成本效益评估

### 4.1 成本模型

#### 4.1.1 标准工作负载定义

定义标准 API 调用工作负载为：**100 万输入 token + 20 万输出 token**。

$\text{Cost}_i = P_{\text{in},i} \times 1 + P_{\text{out},i} \times 0.2$

其中 $P_{\text{in},i}$ 和 $P_{\text{out},i}$ 分别为模型 $i$ 的标准输入和输出单价（USD / 1M tokens）。

#### 4.1.2 各模型标准成本（输入数据 + 确定性计算，可直接采用）

| 模型              | 输入价 ($/1M) | 输出价 ($/1M) | 标准成本 ($) | 参与分析范围    |
| --------------- | ---------- | ---------- | -------- | --------- |
| GLM-5.2         | 1.13       | 3.94       | 1.92     | 独立分析引用    |
| DeepSeek V4 Pro | 0.435      | 0.87       | 0.61     | 排除（仅参考）   |
| Qwen3.8         | 2.00       | 6.00       | 3.20     | 排除（仅参考）   |
| Kimi K3         | 3.00       | 15.00      | 6.00     | Pareto 分析 |
| GPT-5.5         | 3.00       | 15.00      | 6.00     | Pareto 分析 |
| Claude Opus 4.8 | 5.00       | 25.00      | 10.00    | Pareto 分析 |
| GPT-5.6 Sol     | 5.00       | 30.00      | 11.00    | Pareto 分析 |
| Claude Fable 5  | 10.00      | 50.00      | 20.00    | Pareto 分析 |

> 价格为官方定价页输入数据（§9.2），标准成本为公式确定性计算，论文中无需复现验证，但需写明工作负载假设（1M 输入 + 0.2M 输出）的理由（典型生产调用比例）。

### 4.2 Pareto 前沿分析

#### 4.2.1 方法

Pareto 前沿定义为：在所有模型中，不存在另一个模型**同时**成本更低且性能更高的模型集合。

模型 $i$ 被 model $k$ 支配当且仅当：

$\text{Cost}_k \leq \text{Cost}_i \quad \text{且} \quad S_k \geq S_i$

且至少一个不等式严格成立。不被任何模型支配的模型构成 Pareto 前沿。

**判定步骤**（代码手实现）：

1. 仅对 5 个完整排名模型（含其 TOPSIS 得分 $S_i$）做两两支配判断
2. 生成 `results/phase6/pareto_frontier.csv`：每行一个模型，标注 成本 / 得分 / 是否被支配 / 被谁支配
3. 输出 Pareto 前沿模型集合

**论文写作提示**：Pareto 前沿通常包含"低价高性能"端与"高价顶级性能"端两类模型；被支配模型（同成本但得分更低，或更贵且得分更低）是"性价比劣质"的直接证据。具体结论以运行结果为准。

> **📊 图表位置【图13｜2D 散点图】**：**性能—成本 Pareto 前沿散点图**。绘制内容：横轴为标准成本（USD，对数刻度可选）、纵轴为 TOPSIS 得分 $S_i$；每个模型一个点并标注名称；前沿点连线成阶梯状（或仅高亮前沿点用强调色+大圆点）；被支配点灰色，可在点旁标注"被 X 支配"。数据来源 `results/phase6/pareto_frontier.csv`。

### 4.3 预算约束选型策略

#### 4.3.1 选型规则

给定预算 $B$（USD / 标准工作负载），推荐规则为：

$i^*(B) = \arg\max_{\{i:\ \text{Cost}_i \leq B,\ i \in \text{ranked}\}} S_i$

即选择预算内综合得分最高的模型。不排名模型（GLM-5.2）不参与推荐（其性价比定位在 §2.6.2 定性讨论）。

#### 4.3.2 预算档位与输出要求

预设预算档位：$B \in \{6,\ 10,\ 12,\ 16,\ 20\}$（USD）。运行后生成 `results/phase6/budget_recommendations.csv`，列结构（**数值待填**）：

| 预算 $B$ (USD) | 可选模型数 | 推荐模型 | 得分 | 实际成本 |
| ------------ | ----- | ---- | -- | ---- |
| …（5 行）       | 待填    | 待填   | 待填 | 待填   |

> **📊 图表位置【图14｜2D 阶梯图】**：**预算—选型策略阶梯图**。绘制内容：横轴为预算档位、纵轴为推荐模型的 TOPSIS 得分，用阶梯线连接各档位推荐结果，在切换点（推荐模型变化处）标注模型名。数据来源 `results/phase6/budget_recommendations.csv`。

### 4.4 成本—性能变化规律

#### 4.4.1 探索性回归方法

对 5 个完整排名模型拟合对数关系：

$S_i = \beta_0 + \beta_1 \ln(\text{Cost}_i)$

用最小二乘估计 $\beta_0, \beta_1$，计算 $R^2$ 与残差。

**论文写作提示**：若 $R^2$ 偏低（如 <0.5），结论应写为"价格与性能仅弱相关，高价不等于高性能，存在性价比错位"，并用 Pareto 点分布佐证；样本量仅 5，**明确声明不做因果推断，仅描述性规律**。

> **📊 图表位置【图15｜2D 散点 + 拟合曲线】**：**成本—性能对数回归拟合图**。绘制内容：在 §4.2 的 Pareto 散点图基础上叠加对数回归拟合曲线（平滑曲线 + 置信带可选），标注回归方程与 $R^2$。可与图 13 合并为一张图，或单独成图。

### 4.5 工程效率分析

#### 4.5.1 效率数据（输入数据）

仅使用配置兼容（`compatible=true`）的 4 个模型的效率数据：

| 模型              | TTFT (s) | 输出速度 (tokens/s) | 总延迟 (s) | 配置                                             |
| --------------- | -------- | --------------- | ------- | ---------------------------------------------- |
| Kimi K3         | 3.46     | 39.47           | 66.81   | AA default reasoning; Kimi first-party         |
| GPT-5.6 Sol     | 142.43   | 73.74           | 149.21  | max reasoning; OpenAI first-party              |
| Claude Opus 4.8 | 24.74    | 61.06           | 32.93   | Adaptive Reasoning, Max; Anthropic first-party |
| GPT-5.5         | 48.43    | 89.51           | 54.01   | xhigh reasoning; OpenAI first-party            |

> 排除：Claude Fable 5（Opus 4.8 Fallback 混合模型身份）、GLM-5.2（第三方 Together AI 部署，精度未披露）。效率数据测试条件：10k 输入 token；单次 prompt；P50 滚动 72h；标准化 500-token E2E。

#### 4.5.2 效率指标正向化

三个效率指标方向不同，需正向化：

- TTFT：成本型（越小越好）→ $z' = \frac{\max - x}{\max - \min}$
- 输出速度：效益型（越大越好）→ $z' = \frac{x - \min}{\max - \min}$
- 总延迟：成本型 → $z' = \frac{\max - x}{\max - \min}$

#### 4.5.3 部署综合分数

等权平均三个正向化效率指标得到工程效率分 $E_i$，再与性能组合：

$\text{DeployScore}_i = 0.7 \times S_i + 0.3 \times E_i$

**输出物要求**：运行后生成 `results/phase6/deploy_scores.csv`（4 个兼容模型：$E_i$、$\text{DeployScore}_i$，**数值待填**）。论文需对比"纯性能排名 vs 部署综合排名"的变化，说明工程效率对选型的修正作用。

> **📊 图表位置【图16｜2D 分组条形图】**：**工程效率对比图**。绘制内容：4 个兼容模型 ×（TTFT、输出速度、总延迟、部署综合分数）四组标准化条形，或拆为上下两张（上：三个效率指标；下：$S_i$ vs $\text{DeployScore}_i$ 对比）。数据来源 `data/processed/model_attributes.csv` + `results/phase6/deploy_scores.csv`。

### 4.6 三维综合可视化（可选增强）

> **📊 图表位置【图17｜3D 散点图（可选）】**：**性能—成本—效率三维散点图**。绘制内容：X 轴标准成本、Y 轴 TOPSIS 得分、Z 轴工程效率分 $E_i$（或输出速度）；每个模型一个点，点大小或颜色映射第三维度（如模型厂商）；Pareto 前沿点在 Z 方向投影面上加投影线。绘制要求：可旋转视角，附三轴投影。数据来源 §4.1、§4.2、§4.5 结果合并。

> 该图作用：将问题三的"性能、成本、效率"三个评价维度统一到同一空间，支持"高性价比 + 高效率"双优模型的直观识别。

---

## 5 稳健性检验

### 5.1 熵权法对照

#### 5.1.1 方法

用熵权法重新计算权重，验证 CRITIC 结果的稳健性：

**步骤 1**：计算指标 $j$ 的信息熵：

$e_j = -\frac{1}{\ln(m_j)} \sum_{i \in I_j} \frac{z_{ij}}{\sum_{i \in I_j} z_{ij}} \ln\left(\frac{z_{ij}}{\sum_{i \in I_j} z_{ij}}\right)$

**步骤 2**：计算权重：

$w_j^{\text{entropy}} = \frac{1 - e_j}{\sum_k (1 - e_k)}$

**步骤 3**：用熵权法权重重跑 TOPSIS，比较与 CRITIC 权重下的排名一致性（Kendall $\tau$）。

**输出物要求**：运行后生成 `results/phase7/entropy_comparison.csv`（两种方法权重 + 两种排名 + Kendall $\tau$，**数值待填**）。

### 5.2 权重扰动分析

#### 5.2.1 方法

对每个 CRITIC 权重 $w_j$ 分别乘以扰动因子 $\delta \in \{0.8, 0.9, 1.1, 1.2\}$ 后重新归一化，共形成 $9 \times 4 = 36$ 个扰动场景。对每个场景重新执行 TOPSIS，计算与基准排名的 Kendall $\tau$。

**输出物要求**：运行后生成 `results/phase7/perturbation_analysis.csv`（36 行：扰动指标、扰动因子、重归一化权重、新排名、Kendall $\tau$，**数值待填**）。

**论文写作提示**：关注"各模型名次不变的场景数占比"与"最低 $\tau$"，若主要排名在前 3 名保持稳定、最低 $\tau \geq 0.8$，可写"主要结论在给定数据范围内稳健"；任何名次换位需列出具体扰动条件并解释。

> **📊 图表位置【图18｜2D 热力图或箱线图】**：**权重扰动稳健性图**。热力图方案：横轴 9 指标 × 纵轴 4 扰动因子，格内填该扰动下与基准排名的 Kendall $\tau$；箱线图方案：每个模型一个箱，展示 36 个扰动场景下名次分布。数据来源 `results/phase7/perturbation_analysis.csv`。

> **📊 图表位置【表4】**：稳健性检验汇总表，列出熵权法排名对照、扰动场景数、Kendall τ 范围、名次变动情况（数据来源 `results/phase7/*.csv`）。

---

## 6 符号说明

| 符号                                    | 含义                                  |
| ------------------------------------- | ----------------------------------- |
| $m$                                   | 最终模型总数（$m = 6$）                     |
| $n$                                   | 核心指标数（$n = 9$）                      |
| $x_{ij}$                              | 模型 $i$ 在指标 $j$ 上的原始成绩               |
| $z_{ij}$                              | 模型 $i$ 在指标 $j$ 上的标准化值               |
| $w_j$                                 | 指标 $j$ 的 CRITIC 客观权重                |
| $a_{sj}$                              | 场景 $s$ 下指标 $j$ 的主观权重                |
| $w_{sj}^*$                            | 场景 $s$ 下指标 $j$ 的组合权重                |
| $\alpha$                              | 客观权重占比（$\alpha = 0.5$）              |
| $v_{ij}$                              | 加权标准化值（$v_{ij} = w_j \cdot z_{ij}$） |
| $A^+$, $A^-$                          | 正理想解、负理想解                           |
| $D_i^+$, $D_i^-$                      | 模型 $i$ 到正/负理想解的距离                   |
| $S_i$                                 | 模型 $i$ 的 TOPSIS 贴近度（综合得分）           |
| $P_{\text{in},i}$, $P_{\text{out},i}$ | 模型 $i$ 的输入/输出 API 单价（USD/1M tokens） |
| $\text{Cost}_i$                       | 模型 $i$ 的标准工作负载成本                    |
| $B$                                   | 预算约束                                |
| $E_i$                                 | 模型 $i$ 的工程效率分                       |
| $\text{DeployScore}_i$                | 模型 $i$ 的部署综合分数                      |
| $\sigma_j$                            | 指标 $j$ 的标准差                         |
| $r_{jk}$                              | 指标 $j$ 与 $k$ 的 Pearson 相关系数         |
| $C_j$                                 | 指标 $j$ 的信息含量                        |
| $e_j$                                 | 指标 $j$ 的信息熵                         |
| $\Delta_j$                            | 模型与领先者在指标 $j$ 上的差距（§2.6 使用）         |

---

## 7 图表与表格清单（含 2D/3D 类型标注）

| 编号  | 图表名称               | 类型        | 维度     | 对应数据                                                                      | 所在章节 |
| --- | ------------------ | --------- | ------ | ------------------------------------------------------------------------- | ---- |
| 图1  | 技术路线流程图            | 流程图       | 2D     | —                                                                         | §1   |
| 图2  | 指标筛选漏斗图            | 漏斗/结构图    | 2D     | `results/core_indicator_selection.csv`                                    | §2.1 |
| 图3  | Pearson 相关性热力图     | 热力图       | 2D     | `results/phase3/pearson_correlation.csv`                                  | §2.2 |
| 图4  | CRITIC 指标权重条形图     | 条形图       | 2D     | `results/phase4/critic_weights.csv`                                       | §2.3 |
| 图5  | TOPSIS 综合排名条形图     | 条形图       | 2D     | `results/phase4/general_ranking.csv`                                      | §2.4 |
| 图6  | Kimi K3 能力雷达图      | 雷达图       | 2D     | `results/phase4/normalized_scores.csv`                                    | §2.5 |
| 图7  | GLM-5.2 局部能力对比图    | 分组条形图     | 2D     | `data/processed/core_benchmark_matrix.csv`                                | §2.6 |
| 图8  | GLM-5.2 官方 HLE 参照图 | 散点/条形图    | 2D     | `data/raw/benchmark_scores.csv`（Z.ai cohort）                              | §2.6 |
| 图9  | 指标 × 模型得分三维柱状图     | 三维柱状图     | **3D** | `data/processed/core_benchmark_matrix.csv`                                | §2.7 |
| 图10 | 场景排名变化对比图          | 斜率图/分组条形图 | 2D     | `results/phase5/scenario_rankings.csv`                                    | §3.3 |
| 图11 | 场景组合权重热力图          | 热力图       | 2D     | `results/phase5/scenario_weights.csv`                                     | §3.2 |
| 图12 | 场景 × 模型得分三维柱状图     | 三维柱状图     | **3D** | `results/phase5/scenario_rankings.csv`                                    | §3.4 |
| 图13 | 性能—成本 Pareto 前沿散点图 | 散点图       | 2D     | `results/phase6/pareto_frontier.csv`                                      | §4.2 |
| 图14 | 预算—选型策略阶梯图         | 阶梯图       | 2D     | `results/phase6/budget_recommendations.csv`                               | §4.3 |
| 图15 | 成本—性能对数回归拟合图       | 散点 + 曲线   | 2D     | §4.4 回归输出                                                                 | §4.4 |
| 图16 | 工程效率对比图            | 分组条形图     | 2D     | `data/processed/model_attributes.csv`, `results/phase6/deploy_scores.csv` | §4.5 |
| 图17 | 性能—成本—效率三维散点图      | 三维散点图     | **3D** | §4.1/4.2/4.5 合并                                                           | §4.6 |
| 图18 | 权重扰动稳健性图           | 热力图/箱线图   | 2D     | `results/phase7/perturbation_analysis.csv`                                | §5.2 |
| 表1  | 核心指标选取表            | 表格        | —      | `results/core_indicator_selection.csv`                                    | §2.1 |
| 表2  | 高相关指标对审查表          | 表格        | —      | `results/phase3/redundancy_flags.csv`                                     | §2.2 |
| 表3  | 标准化得分明细表           | 表格        | —      | `results/phase4/normalized_scores.csv`                                    | §2.4 |
| 表4  | 稳健性检验汇总表           | 表格        | —      | `results/phase7/*.csv`                                                    | §5   |



> 绘制优先级建议：必画 图1、3、4、5、6、7、10、13、14、18；选画 图2、8、9、11、12、15、16、17（其中 3D 图 9/12/17 建议至少保留 1–2 张以丰富论文可视化层次）。

---

## 8 代码实现指引

### 8.1 代码结构建议

```
scripts/
├── validate_data.py          # 数据校验（来源URL、NA规范、cohort唯一性）
├── check_coverage.py         # 覆盖率检查
├── process_phase2_data.py    # Phase 2 清洗与一致性检查
├── merge_data.py             # 三表合并
├── phase3_correlation.py     # 相关性分析与指标筛选
├── phase4_critic_topsis.py   # CRITIC赋权 + TOPSIS排名 + Kimi优劣势
├── phase4b_glm_analysis.py   # GLM-5.2 局部位次对比与官方HLE参照（§2.6）
├── phase5_scenario.py        # 场景化评价
├── phase6_cost_pareto.py     # 成本效益、Pareto、预算选型、回归、部署分数
├── phase7_robustness.py      # 熵权法对照 + 权重扰动
├── make_figures_2d.py        # 全部 2D 图（SVG）
├── make_figures_3d.py        # 3D 图（图9/12/17，SVG 3D 投影或 matplotlib 导出）
└── run_pipeline.py           # 一键流水线（Phase 2–7 + 图表）
```

### 8.2 关键实现要点

1. **标准化**：对含 NA 的列，min/max 仅对有效值计算
2. **CRITIC**：相关系数矩阵对 NA 用 pairwise deletion
3. **TOPSIS**：仅对 9 项成绩完整的模型（5 个）参与主排名；GLM-5.2 标记 `not_ranked_insufficient_coverage`
4. **GLM-5.2 分析**：只做 4 项局部位次计算 + 官方 HLE 独立引用，**不做任何插补**
5. **场景赋权**：组合后检查 $\sum_j w_{sj}^* = 1$（因两组权重均归一化，线性组合后自动归一化）
6. **Pareto**：只比较 ranked 模型，排除模型不参与
7. **稳健性**：36 个扰动场景循环计算 Kendall τ
8. **3D 图**：若用纯 SVG 实现困难，允许用 matplotlib 导出 PNG（需在文档中说明工具链），坐标轴标注、图例、视角（俯仰角）需在图上写明

### 8.3 输出文件

| 阶段       | 输出目录               | 关键文件                                                                                                                         |
| -------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| Phase 3  | `results/phase3/`  | pearson_correlation.csv, spearman_correlation.csv, indicator_screening.csv, redundancy_flags.csv, descriptive_statistics.csv |
| Phase 4  | `results/phase4/`  | critic_weights.csv, normalized_scores.csv, general_ranking.csv, kimi_strengths_weaknesses.csv                                |
| Phase 4b | `results/phase4b/` | glm_partial_comparison.csv, glm_official_hle_note.csv                                                                        |
| Phase 5  | `results/phase5/`  | scenario_weights.csv, scenario_rankings.csv                                                                                  |
| Phase 6  | `results/phase6/`  | pareto_frontier.csv, budget_recommendations.csv, regression_output.csv, deploy_scores.csv                                    |
| Phase 7  | `results/phase7/`  | entropy_comparison.csv, perturbation_analysis.csv                                                                            |
| 图表       | `figures/`         | 图1–图18（SVG/PNG）                                                                                                              |

### 8.4 运行命令

```bash
python scripts/run_pipeline.py           # 重建 Phase 2–7 结果和全部图表
python -m unittest discover -s tests -v  # 运行测试
```

> 全部脚本仅使用 Python 标准库（3D 图可选 matplotlib，需在 requirements 中注明）。

---

## 9 数据来源汇总

### 9.1 Benchmark 数据来源

| 来源                                            | 类型           | 级别 | URL                                        |
| --------------------------------------------- | ------------ | -- | ------------------------------------------ |
| Kimi K3 官方技术报告                                | 厂商官方报告       | C  | <https://github.com/MoonshotAI/Kimi-K3>    |
| OpenAI GPT-5.6 发布报告                           | 厂商官方报告       | C  | <https://openai.com/index/gpt-5-6/>        |
| Artificial Analysis Intelligence Index v4.1.1 | 独立第三方评测      | A  | <https://artificialanalysis.ai/>           |
| Agents' Last Exam 官方榜单                        | Benchmark 官方 | B  | <https://agents-last-exam.org/leaderboard> |
| Z.ai GLM-5.2 官方发布报告                           | 厂商官方报告       | C  | <https://z.ai/blog/glm-5.2>                |

### 9.2 元数据与价格来源

| 模型                     | 官方来源                                                         |
| ---------------------- | ------------------------------------------------------------ |
| Kimi K3                | <https://www.kimi.com/blog/kimi-k3>                          |
| GPT-5.6 Sol            | <https://developers.openai.com/api/docs/models/gpt-5.6-sol>  |
| Claude Fable 5         | <https://platform.claude.com/docs/en/about-claude/pricing>   |
| Claude Opus 4.8        | <https://platform.claude.com/docs/zh-CN/about-claude/models> |
| GPT-5.5                | <https://developers.openai.com/api/docs/models/compare/>     |
| GLM-5.2                | <https://open.bigmodel.cn/pricing>                           |
| Gemini 3.1 Pro Preview | <https://ai.google.dev/gemini-api/docs/pricing>              |
| DeepSeek V4 Pro 0813   | <https://api-docs.deepseek.com/quick_start/pricing>          |
| Qwen3.8 2.4T A95B      | <https://qwen.ai/blog?id=qwen3.8>                            |

### 9.3 效率数据来源

| 来源                                                        | 类型      | 级别 | URL                                                      |
| --------------------------------------------------------- | ------- | -- | -------------------------------------------------------- |
| Artificial Analysis API Provider Performance Benchmarking | 独立第三方评测 | A  | <https://artificialanalysis.ai/models/{model}/providers> |

> 效率数据测试条件：10k 输入 token；单次 prompt；P50 滚动 72h；标准化 500-token E2E。

---

## 10 注意事项与交接说明

### 10.1 数据红线

1. **禁止自行调用大模型进行 Benchmark**（赛题明确要求）
2. **禁止插补、估算或从图表肉眼读取缺失值**（NA 统一写 `NA`）
3. **禁止跨 cohort 混用数据**（Kimi 报告 cohort 和 OpenAI 发布 cohort 不合并）
4. **禁止将 `compatible=false` 的数据进入严格横向比较**

### 10.2 GLM-5.2 特殊处理

- 冻结主 cohort 中仅有 4/9 项成绩，**不参与 TOPSIS 主排名**，按 §2.6 做单独简要分析
- 官方 HLE 40.5 作为独立 Z.ai cohort 保留，**仅定性参照，不替换主 cohort 的 NA**
- 4 项视觉指标（MMMU-Pro、OmniDocBench、CharXiv RQ、MathVision）因纯文本模型而结构性不适用
- 论文中需明确"数据不足、不参与主排名，但依据可得数据给出局部评价"，不能误写为"低性能"，也不得凭空给出综合排名

### 10.3 Claude Fable 5 效率数据

- AA 标注 Opus 4.8 Fallback，可能混合模型身份
- 效率记录标记 `compatible=false`，仅作补充
- 能力成绩不受影响（来自固定 cohort 对照表）

### 10.4 建模手重点

1. 问题一核心是 **CRITIC + TOPSIS** 的完整推导，需写清标准化、赋权、理想解、贴近度每一步
2. **GLM-5.2 单独分析（§2.6）**&#x5FC5;须写入论文，作为数据不完整模型的处理示范
3. 问题二核心是 **组合赋权** 的设计逻辑，需论证主观权重设定的合理性
4. 问题三核心是 **Pareto 前沿 + 预算选型**，需定义标准工作负载并解释成本计算
5. 所有结果数值等代码手运行后填入，论文初稿先用占位符

### 10.5 代码手重点

1. 脚本只用 Python 标准库（3D 图可选 matplotlib），不引入 numpy/pandas（仓库现有设计）
2. `run_pipeline.py` 可一键重建全部结果，先跑通再改
3. 图表按 §7 清单逐个生成，2D 图统一 SVG 风格；3D 图（图9/12/17）标注坐标轴、图例、视角
4. 所有中间结果 CSV 已存在，代码手可对照验证；新输出（pareto_frontier.csv、deploy_scores.csv、glm_partial_comparison.csv 等）按 §8.3 命名

---

> **文档版本**：v1.1
>
> **更新日期**：2026-08-17
>
> **更新说明**：v1.1 — ① 新增 §2.6 GLM-5.2 单独简要分析（含专属图7/8）；② 移除全部具体结果数值，改为输出物要求（待代码手运行后填写）；③ 图表位置标注升级为明确图类型并覆盖 2D/3D（新增 3D 图9/12/17），图表清单增加维度列。
>
> **数据仓库**：<https://github.com/semiconductor007/Mathematical-Modeling-Data>
