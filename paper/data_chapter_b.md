# B 题数据章节（Member B：模型精确版本、官方元数据、API 可用性与价格）

> 数据截面 `DATA_CUTOFF_DATE = 2026-08-17`；本表数据均检索于 **2026-08-16**，来源见 §4。
> 价格单位统一为 **USD / 1M tokens**；`NA` 表示官方未披露或本次检索未确认，未做任何插补。
> 对应结构化数据：`data/raw/model_metadata.csv`、`data/sources/metadata_sources.csv`、`data/model_candidates.csv`。

## 1. 候选模型精确版本

| model_id | 厂商 | 模型 | 精确版本 / API ID | 发布日期 | 状态 |
|---|---|---|---|---|---|
| kimi-k3 | Moonshot AI | Kimi K3 | Kimi K3 | 2026-07-16 | likely（题目指定必选）|
| gpt-5.6-sol | OpenAI | GPT-5.6 Sol | GPT-5.6 Sol | NA | likely |
| claude-opus-4-8 | Anthropic | Claude Opus 4.8 | claude-opus-4-8 | 2026-05-28 | likely |
| gemini-3.1-pro | Google | Gemini 3.1 Pro | gemini-3.1-pro-preview | NA | likely |
| deepseek-v4-pro | DeepSeek | DeepSeek V4 Pro | DeepSeek-V4-Pro-0813 | 2026-08-13 | likely |
| qwen3.8-max | Alibaba (Qwen) | Qwen3.8-Max | Qwen3.8-Max | 2026-08-03 | likely |
| glm-5.2 | Zhipu AI | GLM-5.2 | GLM-5.2 | NA | likely |
| grok-4.6 | xAI | Grok 4.6 | grok-4.6 | 2026-08-12 | likely |

> 候选池覆盖国内外厂商（国内：Moonshot / DeepSeek / Alibaba / Zhipu；国外：OpenAI / Anthropic / Google / xAI），兼顾前沿与高性价比档位，便于后续"性能—成本"分析。最终 6–8 个名单待团队评审。

## 2. 官方工程元数据

| model_id | 上下文窗口 | 最大输出 | 视觉输入 | 推理支持 | API 可用 |
|---|---|---|---|---|---|
| kimi-k3 | 1,048,576 | 33,000* | 是（文/图/视频）| 是（默认 max）| 是 |
| gpt-5.6-sol | 1,050,000 | 128,000 | 是 | 是 | 是 |
| claude-opus-4-8 | 1,000,000 | 128,000 | 是 | 是（自适应思考）| 是 |
| gemini-3.1-pro | 2,000,000 | NA | 是 | 是 | 是 |
| deepseek-v4-pro | 1,000,000 | 384,000 | 否（纯文本）| 是（默认思考）| 是 |
| qwen3.8-max | 1,000,000 | 65,536 | 是（文/图）| 是（思考模式）| 是 |
| glm-5.2 | 1,048,576 | 128,000 | NA | 是 | 是 |
| grok-4.6 | 500,000 | NA | 是（文/图）| 是（low~xhigh）| 是 |

\* Kimi K3 最大输出 33K 仅来自二级聚合来源，官方博客未列，待确认。

## 3. API 可用性与价格（USD / 1M tokens）

标准价（输入 / 缓存输入 / 输出）：

| model_id | 输入 | 缓存输入 | 输出 | Batch（输入/输出）| 长上下文输入价 | 峰/谷输入价 | 生效日期 |
|---|---|---|---|---|---|---|---|
| kimi-k3 | 3.00 | 0.30 | 15.00 | NA / NA | NA | NA / NA | 2026-07-16 |
| gpt-5.6-sol | 5.00 | 0.50 | 30.00 | 2.50 / 15.00 | NA* | NA / NA | 2026-08-16 |
| claude-opus-4-8 | 5.00 | 0.50 | 25.00 | 2.50 / 12.50 | NA | NA / NA | 2026-05-28 |
| gemini-3.1-pro | 2.00 | 0.20 | 12.00 | 1.00 / 6.00 | 4.00（>200K；输出 18.00）| NA / NA | 2026-08-16 |
| deepseek-v4-pro | 0.435 | 0.003625 | 0.87 | NA / NA | NA | 0.44 / 0.22（输出 1.32 / 0.66）| 2026-08-16 |
| qwen3.8-max | 2.00 | 0.25 | 6.00 | NA / NA | NA | NA / NA | 2026-08-03 |
| glm-5.2 | 1.13† | 0.28† | 3.94† | NA / NA | NA | NA / NA | 2026-08-09 |
| grok-4.6 | 2.00 | 0.50 | 6.00 | NA / NA | 4.00（≥200K；输出 12.00）| NA / NA | 2026-08-12 |

\* OpenAI 对 >270K 上下文另有长上下文档，检索时未抓全具体值，记 NA 待补。
† GLM-5.2 官方挂牌为人民币（¥8 / ¥28 / ¥2），按 7.10 CNY/USD 折算为 USD；原始 CNY 保留于来源表。

**价格条件摘要（避免把有条件价格当统一价）：**
- OpenAI：标准价适用上下文 <270K；区域（数据驻留）端点 +10%；Batch 5 折。
- Anthropic：1M 上下文标准价、无长上下文附加费；缓存读取 = 输入 10%；Batch 5 折。
- Google：按 prompt 长度分档（≤200K vs >200K），上表"长上下文输入价"对应 >200K 档；Batch 5 折。
- DeepSeek：2026-08-16 16:00 UTC 起峰谷计费（峰值 ¥/$（缓存未命中）输入 0.44、输出 1.32；谷值 0.22、0.66）。
- 阿里 Qwen3.8-Max：海外价 $2/$6（与国际可比）；国内价 ¥12/¥36，勿混用。
- xAI Grok 4.6：短文（<200K 输入）$2/$0.50/$6；长文（≥200K）$4/$1/$12；无 Batch 折扣，但 Priority Processing 为 2× 标准价。

## 4. 来源整理

每个数值均登记于 `data/sources/metadata_sources.csv`（共 71 条逐字段证据）。核心一手来源（厂商官方）：

| 模型 | 官方来源 |
|---|---|
| Kimi K3 | https://www.kimi.com/blog/kimi-k3 ；API https://platform.kimi.ai/ |
| GPT-5.6 Sol | https://developers.openai.com/api/docs/models/compare/ ；https://platform.openai.com/docs/pricing/ |
| Claude Opus 4.8 | https://platform.claude.com/docs/zh-CN/about-claude/models |
| Gemini 3.1 Pro | https://ai.google.dev/gemini-api/docs/pricing |
| DeepSeek V4 Pro | https://api-docs.deepseek.com/quick_start/pricing |
| Qwen3.8-Max | https://qwen.ai/blog?id=qwen3.8 （价格见 Global Times 发布报道 https://www.globaltimes.cn/page/202608/1367420.shtml ）|
| GLM-5.2 | https://open.bigmodel.cn/pricing |
| Grok 4.6 | https://docs.x.ai/developers/pricing ；https://x.ai/news/grok-4-6 |

**来源优先级**：厂商官方文档/模型卡（Level C）＞ Benchmark 官方/统一评测（Level B）＞ 独立第三方横向评测（Level A）＞ 二手资料（Level D，仅辅助）。本章节价格均取自官方页或官方发布报道，未采用搜索摘要或截图作为核心依据。

## 5. 数据质量与待确认项

- 缺失统一记 `NA`，未插补、未估算。
- 待确认：`gpt-5.6-sol`/`gemini-3.1-pro`/`glm-5.2` 发布日期；GLM-5.2 最大输出 128K vs 262K 冲突；Kimi K3 最大输出（单一二级来源）；OpenAI >270K 长上下文具体费率。
- `model_id` 由本分支先行定义，需 Member A 的 Benchmark 数据使用同一标识以保证可合并。
