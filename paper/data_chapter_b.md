# B 题数据章节（Member B：模型精确版本、官方元数据、API 可用性与价格）

> 数据截面 `DATA_CUTOFF_DATE = 2026-08-17`；本表数据均检索于 **2026-08-16**，来源见 §4。
> 价格单位统一为 **USD / 1M tokens**；`NA` 表示官方未披露或本次检索未确认，未做任何插补。
> 对应结构化数据：`data/raw/model_metadata.csv`、`data/sources/metadata_sources.csv`、`data/model_candidates.csv`。

## 1. 候选模型精确版本

候选池共 9 个；Phase 1 最终冻结 6 个：

| model_id | 厂商 | 模型 | 精确版本 / slug | 发布日期 | 状态 |
|---|---|---|---|---|---|
| kimi-k3 | Moonshot AI | Kimi K3 | kimi-k3 | 2026-07-16 | final（题目指定必选）|
| gpt-5.6-sol | OpenAI | GPT-5.6 Sol | gpt-5.6-sol | 2026-07-09 | final |
| claude-fable-5 | Anthropic | Claude Fable 5 | claude-fable-5 | 2026-06-09 | final |
| claude-opus-4.8 | Anthropic | Claude Opus 4.8 | claude-opus-4.8 | 2026-05-28 | final |
| gpt-5.5 | OpenAI | GPT-5.5 | gpt-5.5 | 2026-04-23 | final |
| glm-5.2 | Z.ai | GLM-5.2 | GLM-5.2 | 2026-06-16 | final |
| gemini-3.1-pro-preview | Google | Gemini 3.1 Pro Preview | gemini-3.1-pro-preview | 2026-02-19 | excluded |
| deepseek-v4-pro-0813 | DeepSeek | DeepSeek V4 Pro 0813 | DeepSeek V4 Pro 0813 | 2026-08-13 | excluded |
| qwen3.8-2.4t-a95b | Alibaba | Qwen3.8 2.4T A95B | Qwen3.8 2.4T A95B | 2026-08-12 | excluded |

> 候选池覆盖国内外厂商（国内：Moonshot / DeepSeek / Alibaba / Z.ai；国外：OpenAI / Anthropic / Google），兼顾前沿与高性价比档位，便于后续"性能—成本"分析。所有 `model_id`、`model_name`、`provider`、`exact_version`、`release_date` 均与 Member A 的 `model_candidates.csv` 严格一致，保证三张原始表可按 `model_id` 合并。

## 2. 官方工程元数据

| model_id | 上下文窗口 | 最大输出 | 视觉输入 | 推理支持 | API 可用 |
|---|---|---|---|---|---|
| kimi-k3 | 1,048,576 | 33,000* | 是（文/图/视频）| 是（默认 max）| 是 |
| gpt-5.6-sol | 1,050,000 | 128,000 | 是 | 是（max）| 是 |
| claude-fable-5 | 1,000,000 | 128,000 | 是 | 是（自适应思考）| 是 |
| claude-opus-4.8 | 1,000,000 | 128,000 | 是 | 是（自适应思考）| 是 |
| gpt-5.5 | 256,000 | 128,000 | 是 | 是（xhigh）| 是 |
| glm-5.2 | 1,048,576 | 128,000 | NA | 是 | 是 |
| gemini-3.1-pro-preview | 2,000,000 | NA | 是 | 是 | 是 |
| deepseek-v4-pro-0813 | 1,000,000 | 384,000 | 否（纯文本）| 是（默认思考）| 是 |
| qwen3.8-2.4t-a95b | 1,000,000 | 65,536 | 是（文/图）| 是（思考模式）| 是 |

\* Kimi K3 最大输出 33K 仅来自二级聚合来源，官方博客未列，待确认。

## 3. API 可用性与价格（USD / 1M tokens）

标准价（输入 / 缓存输入 / 输出）：

| model_id | 输入 | 缓存输入 | 输出 | Batch（输入/输出）| 长上下文输入价 | 峰/谷输入价 | 生效日期 |
|---|---|---|---|---|---|---|---|
| kimi-k3 | 3.00 | 0.30 | 15.00 | NA / NA | NA | NA / NA | 2026-07-16 |
| gpt-5.6-sol | 5.00 | 0.50 | 30.00 | 2.50 / 15.00 | NA* | NA / NA | 2026-07-09 |
| claude-fable-5 | 8.00 | 0.80 | 40.00 | 4.00 / 20.00 | NA | NA / NA | 2026-06-09 |
| claude-opus-4.8 | 5.00 | 0.50 | 25.00 | 2.50 / 12.50 | NA | NA / NA | 2026-05-28 |
| gpt-5.5 | 3.00 | 0.30 | 15.00 | 1.50 / 7.50 | NA | NA / NA | 2026-04-23 |
| glm-5.2 | 1.13† | 0.28† | 3.94† | NA / NA | NA | NA / NA | 2026-06-16 |
| gemini-3.1-pro-preview | 2.00 | 0.20 | 12.00 | 1.00 / 6.00 | 4.00（>200K；输出 18.00）| NA / NA | 2026-02-19 |
| deepseek-v4-pro-0813 | 0.435 | 0.003625 | 0.87 | NA / NA | NA | 0.44 / 0.22（输出 1.32 / 0.66）| 2026-08-13 |
| qwen3.8-2.4t-a95b | 2.00 | 0.25 | 6.00 | NA / NA | NA | NA / NA | 2026-08-12 |

\* OpenAI 对 GPT-5.6 Sol >270K 上下文另有长上下文档，检索时未抓全具体值，记 NA 待补。GPT-5.5 无单独长上下文分档。
† GLM-5.2 官方挂牌为人民币（¥8 / ¥28 / ¥2），按 7.10 CNY/USD 折算为 USD；原始 CNY 保留于来源表。

**价格条件摘要（避免把有条件价格当统一价）：**
- OpenAI：标准价适用上下文 <270K；区域（数据驻留）端点 +10%；Batch 5 折。GPT-5.5 为成熟基线，定价低于 GPT-5.6 Sol。
- Anthropic：1M 上下文标准价、无长上下文附加费；缓存读取 = 输入 10%；Batch 5 折。Fable 5 为最高档，定价高于 Opus 4.8。
- Google：按 prompt 长度分档（≤200K vs >200K），上表"长上下文输入价"对应 >200K 档；Batch 5 折。
- DeepSeek：2026-08-16 16:00 UTC 起峰谷计费（峰值输入 0.44、输出 1.32；谷值 0.22、0.66，均为缓存未命中口径）。
- 阿里 Qwen3.8 2.4T A95B：海外价 $2/$6（与国际可比）；国内价 ¥12/¥36，勿混用。

## 4. 来源整理

每个数值均登记于 `data/sources/metadata_sources.csv`（共 79 条逐字段证据）。核心一手来源（厂商官方）：

| 模型 | 官方来源 |
|---|---|
| Kimi K3 | https://www.kimi.com/blog/kimi-k3 ；API https://platform.kimi.ai/ |
| GPT-5.6 Sol | https://developers.openai.com/api/docs/models/compare/ ；https://platform.openai.com/docs/pricing/ |
| Claude Fable 5 | https://platform.claude.com/docs/zh-CN/about-claude/models |
| Claude Opus 4.8 | https://platform.claude.com/docs/zh-CN/about-claude/models |
| GPT-5.5 | https://developers.openai.com/api/docs/models/compare/ ；https://platform.openai.com/docs/pricing/ |
| GLM-5.2 | https://open.bigmodel.cn/pricing |
| Gemini 3.1 Pro Preview | https://ai.google.dev/gemini-api/docs/pricing |
| DeepSeek V4 Pro 0813 | https://api-docs.deepseek.com/quick_start/pricing |
| Qwen3.8 2.4T A95B | https://qwen.ai/blog?id=qwen3.8 （价格见 Global Times 发布报道 https://www.globaltimes.cn/page/202608/1367420.shtml ）|

**来源优先级**：统一独立第三方横向评测（Level A）＞ Benchmark 官方榜单（Level B）＞ 厂商官方文档/模型卡（Level C）＞ 二手资料（Level D，仅辅助）。元数据和价格优先采用对应厂商官方页，未采用搜索摘要或截图作为核心依据。

## 5. 数据质量与待确认项

- 缺失统一记 `NA`，未插补、未估算。
- **待确认**：GLM-5.2 最大输出 128K vs 262K 冲突；Kimi K3 最大输出（单一二级来源）；OpenAI GPT-5.6 Sol >270K 长上下文具体费率。
- **Claude Fable 5 fallback 风险**：AA 明示 Opus 4.8 Fallback，因此效率记录保留但标记 `compatible=false`；该限制不影响固定 cohort 的能力成绩。
- `model_id` 已与 Member A 完全对齐（本轮修正 4 个 ID、6 个 exact_version、4 个 release_date、2 个 provider、3 个 model_name；新增 2 个模型；移除 1 个不在候选池中的模型）。
