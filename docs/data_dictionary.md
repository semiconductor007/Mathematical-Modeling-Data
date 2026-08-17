# 数据字典

问题1建模输入为 `data/processed/core_benchmark_long.csv`。每行表示一个“最终模型—冻结指标”观测；模型标识和来源字段为文本，`score` 为数值或 `NA`。成本、时延和吞吐来自 `model_attributes.csv`，只为问题3预留，不进入问题1纯性能排名。

## 问题1性能指标

| 指标名称 | 英文/代码字段名 | 指标含义 | 指标类别 | 单位 | 方向 | 数据来源 | 是否进入问题1 | 备注 |
|---|---|---|---|---|---|---|---|---|
| GPQA Diamond | `gpqa_diamond` | 研究生水平科学问答，衡量高难度知识推理能力 | 高难度知识与逻辑推理 | percent | 正向 | Kimi K3 official technical report | 是 | 缺失不插补；按冻结 cohort 比较 |
| HLE-Full | `hle_full_no_tools` | Humanity's Last Exam 无工具成绩，衡量极高难度开放推理 | 高难度知识与逻辑推理 | percent | 正向 | Kimi K3 official technical report | 是 | 缺失不插补；按冻结 cohort 比较 |
| AA-LCR | `aa_lcr` | Artificial Analysis 长上下文推理成绩 | 长文本理解与推理 | percent | 正向 | Kimi K3 official technical report | 是 | 缺失不插补；按冻结 cohort 比较 |
| SciCode | `scicode` | 科学研究代码生成与求解能力 | 代码与科学编程 | percent | 正向 | Kimi K3 official technical report | 是 | 缺失不插补；按冻结 cohort 比较 |
| GDPval-AA v2 | `gdpval_aa_v2` | 专业知识工作任务的相对能力评分 | 专业任务能力 | elo | 正向 | Kimi K3 official technical report | 是 | 缺失不插补；按冻结 cohort 比较 |
| MMMU-Pro | `mmmu_pro_no_tools` | 无工具多学科多模态理解能力 | 多模态理解 | percent | 正向 | Kimi K3 official technical report | 是 | 缺失不插补；按冻结 cohort 比较 |
| OmniDocBench | `omnidocbench` | 复杂文档解析与理解能力 | 文档理解 | percent | 正向 | Kimi K3 official technical report | 是 | 缺失不插补；按冻结 cohort 比较 |
| CharXiv RQ | `charxiv_rq_no_tools` | 科研论文图表与问题推理能力 | 科研文档推理 | percent | 正向 | Kimi K3 official technical report | 是 | 缺失不插补；按冻结 cohort 比较 |
| MathVision | `mathvision_no_tools` | 无工具视觉数学推理能力 | 多模态数学推理 | percent | 正向 | Kimi K3 official technical report | 是 | 缺失不插补；按冻结 cohort 比较 |

## 标识、来源与工程字段

| 字段名 | 含义 | 类别 | 单位 | 方向 | 是否进入问题1 | 备注 |
|---|---|---|---|---|---|---|
| `model_id` / `model_name` | 模型唯一标识与展示名 | 文本标识 | — | — | 仅保留标识 | 不参与数值计算 |
| `source_name` / `source_url` / `retrieval_date` | 指标来源与检索日期 | 来源字段 | — | — | 否 | 用于追溯 |
| `input_price_usd_per_million` / `output_price_usd_per_million` | API 输入/输出价格 | 成本 | USD/1M tokens | 负向 | 否 | 问题3使用 |
| `comparable_ttft_seconds` | 首 token 延迟 | 工程效率 | seconds | 负向 | 否 | 问题3使用；仅 compatible 记录 |
| `comparable_output_speed_tokens_per_second` | 输出速度 | 工程效率 | tokens/s | 正向 | 否 | 问题3使用；仅 compatible 记录 |
| `comparable_total_latency_seconds` | 标准响应总延迟 | 工程效率 | seconds | 负向 | 否 | 问题3使用；仅 compatible 记录 |

当前工程属性表含 6 个最终模型。仓库没有可严格横向比较的能耗字段，因此问题1和现阶段问题3接口均不虚构能耗数值。
