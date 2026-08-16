# 模型元数据与价格调研记录（Member B）

记录官方页面、精确版本、字段歧义、价格地区/套餐/生效时间、历史变更和来源冲突。
结构化记录已分别写入 `data/raw/model_metadata.csv` 与 `data/sources/metadata_sources.csv`。
检索日期统一为 **2026-08-16**，数据截面 `DATA_CUTOFF_DATE = 2026-08-17`，所有资料均在该截面之前公开。

## 1. 候选模型池与 model_id 约定

候选池（8 个，覆盖国内外厂商，Kimi K3 按要求必选）：

| model_id | 厂商 | 模型 | 地区 |
|---|---|---|---|
| kimi-k3 | Moonshot AI | Kimi K3 | 国内 |
| gpt-5.6-sol | OpenAI | GPT-5.6 Sol | 国外 |
| claude-opus-4-8 | Anthropic | Claude Opus 4.8 | 国外 |
| gemini-3.1-pro | Google | Gemini 3.1 Pro Preview | 国外 |
| deepseek-v4-pro | DeepSeek | DeepSeek V4 Pro | 国内 |
| qwen3.8-max | Alibaba (Qwen) | Qwen3.8-Max | 国内 |
| glm-5.2 | Zhipu AI | GLM-5.2 | 国内 |
| grok-4.6 | xAI | Grok 4.6 | 国外 |

**一致性约定**：`model_id` 采用小写 kebab 形式，由本分支（Member B）先行定义，**请 Member A 在 `benchmark_scores.csv` 与 `model_candidates.csv` 中使用同一 `model_id`**，以保证三张原始表可按 `model_id` 合并（`scripts/merge_data.py`）。若 Member A 采用不同命名，需在合并前统一。

## 2. 价格单位与折算

- 所有价格统一为 **USD / 1M tokens**（DATA_RULES §5）。
- **智谱 GLM-5.2** 官方挂牌价为人民币：输入 ¥8 / 输出 ¥28 / 缓存命中 ¥2（每百万）。按检索日近似汇率 **7.10 CNY/USD** 折算为 $1.13 / $3.94 / $0.28，并记录原始 CNY 于本文件与来源表，转换可复现。
- 阿里 **Qwen3.8-Max** 海外价为 $2/$6、隐式缓存命中 $0.25；国内价为 ¥12/¥36、缓存命中 ¥1.5。已采用**海外价**（与国际模型可比），并在 `notes` 注明国内价差异。

## 3. 字段歧义与不确定项

- **Kimi K3 最大输出**：官方博客未给出；33K 仅来自二级聚合站（swfte.com），已标注为单一来源并保留 `33000`，建议团队确认。
- **Gemini 3.1 Pro 上下文窗口**：官方定价文档只列出 `>200K` 分档而未直接打印窗口数字；2M 来自模型卡与二级来源，已采用 `2000000` 并注明。
- **Gemini 3.1 Pro 最大输出**：检索来源均未给出 → `NA`。
- **Grok 4.6 最大输出**：官方未公布上限 → `NA`。
- **GLM-5.2 最大输出**：官方定价页镜像给 128K，OpenRouter 给 262K，**存在冲突**；采用 128K（官方页口径）并在本文件记录冲突，待团队裁定。
- **GLM-5.2 视觉支持**：未明确确认（GLM-5.1 文献记为纯文本）→ `NA`，未臆测。
- **发布日期缺失**：`gpt-5.6-sol`、`gemini-3.1-pro`、`glm-5.2` 的发布日期在检索来源中未确认 → `NA`，已 flag 待 Member A / 团队补全。

## 4. 套餐 / 区域 / 上下文 / 缓存条件（避免把有条件价格当统一价）

- **OpenAI**：标准价为上下文 <270K 的费率；>270K 另有长上下文档，检索时未抓全具体值 → `long_context_price = NA`（待补）。区域（数据驻留）端点 +10%。Batch = 5 折。
- **Anthropic**：1M 上下文按标准价计费、无长上下文附加费；Prompt 缓存读取 = 输入的 10%（Opus 4.8 缓存输入 $0.50）；Batch = 5 折；无峰谷。
- **Google Gemini 3.1 Pro**：按 prompt 长度分档——≤200K 输入 $2/输出 $12/缓存 $0.20；>200K 输入 $4/输出 $18/缓存 $0.40。`long_context_price` 记录 >200K 输入价 $4.00，输出 $18.00 见 `notes`。Batch = 5 折。
- **DeepSeek V4 Pro**：自 **2026-08-16 16:00 UTC** 起实行峰谷计费——**峰** 输入 $0.44/输出 $1.32，**谷** 输入 $0.22/输出 $0.66（均为缓存未命中口径）；`peak_price`/`off_peak_price` 记录缓存未命中输入价，输出见 `notes`。表内 `input_price` 等为主表缓存未命中标准价。无明确 Batch 折扣。
- **阿里 Qwen3.8-Max**：海外与国际模型可比价 $2/$6；国内价显著不同，勿混用。无 Batch / 长上下文分档（1M 标准价）。
- **xAI Grok 4.6**：短文（<200K 输入）输入 $2/缓存 $0.50/输出 $6；长文（≥200K）输入 $4/缓存 $1/输出 $12，`long_context_price` 记 $4.00。`peak/off-peak` 不适用，但 **Priority Processing 为 2× 标准价**，已在 `notes` 说明。4.6 不在 Batch 折扣表 → `NA`。

## 5. 来源冲突与可靠性

- 多数价格来自**厂商官方文档/模型卡**（Level C，最高优先级）。
- 价格数值均要求"直接支撑该数字"的 `source_url`；搜索摘要、截图、营销文未作为核心来源。
- 二级来源（swfte、llmcostcalc、aitooltier 等）仅用于填补官方页缺失字段（如 Kimi K3 最大输出、GLM 最大输出），并已明确标注。
- 智谱价格以官方 CNY 挂牌为基准，USD 为折算值，原始值保留。

## 6. 待团队确认 / 后续

1. 与 Member A 对齐 `model_id` 命名与最终 6–8 个名单（当前 8 个均 `likely`，尚未 `final`）。
2. 补全 `gpt-5.6-sol`、`gemini-3.1-pro`、`glm-5.2` 发布日期。
3. 裁定 GLM-5.2 最大输出 128K vs 262K 冲突。
4. 补全 OpenAI >270K 长上下文具体费率。
5. 确认 Kimi K3 最大输出（当前单一二级来源）。
6. 汇率 7.10 为检索日近似；若论文要求，可统一改用论文截稿日官方中间价并重算。
