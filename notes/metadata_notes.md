# 模型元数据与价格调研记录（Member B）

记录官方页面、精确版本、字段歧义、价格地区/套餐/生效时间、历史变更和来源冲突。
结构化记录已分别写入 `data/raw/model_metadata.csv` 与 `data/sources/metadata_sources.csv`。
检索日期统一为 **2026-08-16**，数据截面 `DATA_CUTOFF_DATE = 2026-08-17`，所有资料均在该截面之前公开。

**Phase 1 冻结说明**：9 个候选的身份、元数据与价格已逐字段核验并对齐。最终模型池采用 Kimi K3、GPT-5.6 Sol、Claude Fable 5、Claude Opus 4.8、GPT-5.5、GLM-5.2；其余 3 个候选的资料继续保留用于审计。条件价格与未披露字段保持 `NA`，不推断、不插补。

## 1. 候选模型池与 model_id 约定

**本轮更新（2026-08-16 第二版）**：已与 Member A 的 `data-benchmark` 分支完全对齐。B 的候选池从原来的 8 个调整为 A 的 9 个，所有 `model_id`、`model_name`、`provider`、`exact_version`、`release_date` 均与 A 一致。

候选池（9 个，覆盖国内外厂商，Kimi K3 按要求必选）：

| model_id | 厂商 | 模型 | 精确版本 | 发布日期 | 状态 |
|---|---|---|---|---|---|
| kimi-k3 | Moonshot AI | Kimi K3 | kimi-k3 | 2026-07-16 | final |
| gpt-5.6-sol | OpenAI | GPT-5.6 Sol | gpt-5.6-sol | 2026-07-09 | final |
| claude-fable-5 | Anthropic | Claude Fable 5 | claude-fable-5 | 2026-06-09 | final |
| claude-opus-4.8 | Anthropic | Claude Opus 4.8 | claude-opus-4.8 | 2026-05-28 | final |
| gpt-5.5 | OpenAI | GPT-5.5 | gpt-5.5 | 2026-04-23 | final |
| glm-5.2 | Z.ai | GLM-5.2 | GLM-5.2 | 2026-06-16 | final |
| gemini-3.1-pro-preview | Google | Gemini 3.1 Pro Preview | gemini-3.1-pro-preview | 2026-02-19 | excluded |
| deepseek-v4-pro-0813 | DeepSeek | DeepSeek V4 Pro 0813 | DeepSeek V4 Pro 0813 | 2026-08-13 | excluded |
| qwen3.8-2.4t-a95b | Alibaba | Qwen3.8 2.4T A95B | Qwen3.8 2.4T A95B | 2026-08-12 | excluded |

**一致性约定**：`model_id` 采用小写 kebab 形式，与 Member A 的 `model_candidates.csv` 和 `benchmark_scores.csv` 完全一致，保证三张原始表可按 `model_id` 合并（`scripts/merge_data.py`）。

### 本轮修正明细（vs 第一版）

| 修正项 | 旧值 | 新值 | 原因 |
|---|---|---|---|
| claude-opus-4-8 model_id | claude-opus-4-8 | claude-opus-4.8 | A 使用点号分隔，须严格一致 |
| gemini-3.1-pro model_id | gemini-3.1-pro | gemini-3.1-pro-preview | A 含 -preview 后缀 |
| deepseek-v4-pro model_id | deepseek-v4-pro | deepseek-v4-pro-0813 | A 含 -0813 版本戳 |
| qwen3.8-max model_id | qwen3.8-max | qwen3.8-2.4t-a95b | A 的 model_id 与 B 完全不同；qwen3.8-max 是另一候选 |
| claude-opus-4.8 exact_version | Claude Opus 4.8 (API ID claude-opus-4-8) | claude-opus-4.8 | 与 A slug 严格一致 |
| gemini model_name | Gemini 3.1 Pro | Gemini 3.1 Pro Preview | 与 A 一致 |
| gemini exact_version | Gemini 3.1 Pro Preview (gemini-3.1-pro-preview) | gemini-3.1-pro-preview | 与 A slug 严格一致 |
| deepseek model_name | DeepSeek V4 Pro | DeepSeek V4 Pro 0813 | 与 A 一致 |
| deepseek exact_version | DeepSeek-V4-Pro-0813 | DeepSeek V4 Pro 0813 | 与 A 显示名一致 |
| qwen model_name | Qwen3.8-Max | Qwen3.8 2.4T A95B | 与 A 一致 |
| qwen exact_version | Qwen3.8-Max | Qwen3.8 2.4T A95B | 与 A 一致 |
| qwen provider | Alibaba (Qwen Team / QwenCloud / DashScope) | Alibaba | 与 A 一致 |
| glm provider | Zhipu AI | Z.ai | 与 A 一致 |
| kimi-k3 exact_version | Kimi K3 | kimi-k3 | 与 A slug 严格一致 |
| gpt-5.6-sol exact_version | GPT-5.6 Sol | gpt-5.6-sol | 与 A slug 严格一致 |
| gpt-5.6-sol release_date | NA | 2026-07-09 | 与 A 一致 |
| gemini release_date | NA | 2026-02-19 | 与 A 一致 |
| qwen release_date | 2026-08-03 | 2026-08-12 | 与 A 一致 |
| glm release_date | NA | 2026-06-16 | 与 A 一致 |

**新增模型**：claude-fable-5（Anthropic 最高档，2026-06-09）、gpt-5.5（OpenAI 成熟基线，2026-04-23）。

**移除模型**：grok-4.6（xAI）。Grok 4.6 不在 A 的 9 个候选模型池中。已收集的数据保留在本文件 §7 作为 B 提议的补充候选备查，但不进入正式 `model_metadata.csv`。

## 2. 价格单位与折算

- 所有价格统一为 **USD / 1M tokens**（DATA_RULES §5）。
- **智谱 GLM-5.2** 官方挂牌价为人民币：输入 ¥8 / 输出 ¥28 / 缓存命中 ¥2（每百万）。按检索日近似汇率 **7.10 CNY/USD** 折算为 $1.13 / $3.94 / $0.28，并记录原始 CNY 于本文件与来源表，转换可复现。
- **阿里 Qwen3.8 2.4T A95B** 海外价为 $2/$6、隐式缓存命中 $0.25；国内价为 ¥12/¥36、缓存命中 ¥1.5。已采用**海外价**（与国际模型可比），并在 `notes` 注明国内价差异。

## 3. 字段歧义与不确定项

- **Kimi K3 最大输出**：官方 API 文档明确 `max_completion_tokens` 默认 131,072、最大可设为 1,048,576，实际最大输出为 `1,048,576 - prompt_tokens`。主表记录 1,048,576 并在备注保留上下文约束；原 33K 二级值已废弃。
- **Gemini 3.1 Pro Preview 上下文窗口**：官方定价文档只列出 `>200K` 分档而未直接打印窗口数字；2M 来自模型卡与二级来源，已采用 `2000000` 并注明。
- **Gemini 3.1 Pro Preview 最大输出**：检索来源均未给出 → `NA`。
- **Grok 4.6 最大输出**：官方未公布上限 → `NA`（见 §7 补充候选）。
- **GLM-5.2 最大输出**：智谱官方 GLM-5.2 模型页明确为 128K，按 `128×1024` 记录为 131,072 tokens。OpenRouter 的 262K 为第三方部署口径，予以废弃，不再构成冻结数据冲突。
- **GLM-5.2 视觉支持**：Z.ai 官方模型卡归类为 Text Generation，仅给出文本生成 pipeline，未列图像输入 → `no`。因此 MMMU-Pro、OmniDocBench、CharXiv RQ、MathVision 的缺失属于结构性不适用。
- **Claude Fable 5 fallback 风险**：AA 明示 Opus 4.8 Fallback；C 审计标记 HOLD，因为现有证据不能证明每次测量均由 Fable 5 执行或分离混合观测。数据保留但需团队裁定是否进入核心模型。

## 4. 套餐 / 区域 / 上下文 / 缓存条件（避免把有条件价格当统一价）

- **OpenAI**：GPT-5.6 Sol 标准价为输入 $5 / 缓存 $0.50 / 输出 $30；输入 prompt 超过 272K 时，整次请求按输入 2 倍、输出 1.5 倍计费，即 $10 / $45，故 `long_context_price = 10.00`。区域（数据驻留）端点 +10%。Batch = 5 折。GPT-5.5 无单独长上下文分档。
- **Anthropic**：1M 上下文按标准价计费、无长上下文附加费；Fable 5 当前官方价为输入 $10 / 缓存命中 $1 / 输出 $50，Batch 为 $5 / $25；Opus 4.8 为 $5 / $0.50 / $25，Batch 为 $2.50 / $12.50；无峰谷。
- **Google Gemini 3.1 Pro Preview**：按 prompt 长度分档——≤200K 输入 $2/输出 $12/缓存 $0.20；>200K 输入 $4/输出 $18/缓存 $0.40。`long_context_price` 记录 >200K 输入价 $4.00，输出 $18.00 见 `notes`。Batch = 5 折。
- **DeepSeek V4 Pro 0813**：自 **2026-08-16 16:00 UTC** 起实行峰谷计费——**峰** 输入 $0.44/输出 $1.32，**谷** 输入 $0.22/输出 $0.66（均为缓存未命中口径）；`peak_price`/`off_peak_price` 记录缓存未命中输入价，输出见 `notes`。表内 `input_price` 等为主表缓存未命中标准价。无明确 Batch 折扣。
- **阿里 Qwen3.8 2.4T A95B**：海外与国际模型可比价 $2/$6；国内价显著不同，勿混用。无 Batch / 长上下文分档（1M 标准价）。

## 5. 来源冲突与可靠性

- 多数价格来自**厂商官方文档/模型卡**（Level C，最高优先级）。
- 价格数值均要求"直接支撑该数字"的 `source_url`；搜索摘要、截图、营销文未作为核心来源。
- 二级来源不再用于 Kimi K3 或 GLM-5.2 最大输出字段；两项均已替换为第一方 API/模型文档。其他二级资料仅作为审计线索，不覆盖第一方数据。
- 智谱价格以官方 CNY 挂牌为基准，USD 为折算值，原始值保留。
- 来源表共 79 条逐字段证据（vs 第一版 71 条），新增的 8 条覆盖 Claude Fable 5 和 GPT-5.5 的 9 个字段（共 18 条）。

## 6. 待团队确认 / 后续

1. ~~与 Member A 对齐 `model_id` 命名~~ ✅ 本轮已完成对齐。
2. ~~补全 `gpt-5.6-sol`、`gemini-3.1-pro-preview`、`glm-5.2` 发布日期~~ ✅ 已与 A 对齐。
3. ~~裁定 GLM-5.2 最大输出 128K vs 262K 冲突~~ ✅ 采用官方 128K（131,072），废弃第三方 262K。
4. ~~补全 OpenAI GPT-5.6 Sol >272K 长上下文具体费率~~ ✅ 已补全为输入 $10 / 输出 $45（整次请求）。
5. ~~确认 Kimi K3 最大输出~~ ✅ 官方 API 明确最大设置 1,048,576，实际为上下文窗口减输入 token。
6. 裁定 Claude Fable 5 是否进入核心模型（C 审计 HOLD：fallback 语义不确定）。
7. 汇率 7.10 为检索日近似；若论文要求，可统一改用论文截稿日官方中间价并重算。

## 7. 补充候选备查：Grok 4.6（xAI）

> 以下数据为 B 第一轮已收集，但 Grok 4.6 不在 A 的 9 个候选模型池中，不进入正式 `model_metadata.csv`。保留备查，若团队后续决定扩充候选池可启用。

| 字段 | 值 | 来源 |
|---|---|---|
| model_id | grok-4.6 | — |
| provider | xAI | https://x.ai/news/grok-4-6 |
| exact_version | Grok 4.6 (grok-4.6) | https://x.ai/news/grok-4-6 |
| release_date | 2026-08-12 | https://x.ai/news/grok-4-6 |
| context_window | 500000 | https://docs.x.ai/developers/pricing |
| max_output_tokens | NA | https://docs.x.ai/developers/pricing |
| vision_support | yes | https://docs.x.ai/developers/pricing |
| reasoning_support | yes (low/medium/high/xhigh) | https://docs.x.ai/developers/pricing |
| api_available | yes | https://docs.x.ai/developers/pricing |
| input_price (short <200K) | $2.00/1M | https://docs.x.ai/developers/pricing |
| output_price (short <200K) | $6.00/1M | https://docs.x.ai/developers/pricing |
| cached_input (short <200K) | $0.50/1M | https://docs.x.ai/developers/pricing |
| long_context (>=200K) input | $4.00/1M (output $12.00) | https://docs.x.ai/developers/pricing |
| batch | NA | https://docs.x.ai/developers/pricing |
| peak/off-peak | NA (Priority Processing 2x) | https://docs.x.ai/developers/pricing |
| pricing_effective_date | 2026-08-12 | https://docs.x.ai/developers/pricing |

xAI 短文（<200K 输入）$2/$0.50/$6；长文（≥200K）$4/$1/$12。4.6 不在 Batch 折扣表。Priority Processing 为 2× 标准价。
