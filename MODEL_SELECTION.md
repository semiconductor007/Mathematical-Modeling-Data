# 候选模型选择规则

本文件定义筛选程序，不凭知名度或“最新”标签直接确定最终名单。Kimi K3 必须进入候选池；其余候选须经公开资料检索后登记。目标候选池为 6–10 个，最终评估预计保留 6–8 个。

## 纳入条件

候选模型应尽量同时满足：主流且有现实使用价值；具有国内外及厂商代表性；在数据截止日前正式公开；名称和版本明确；拥有足够公开 Benchmark；最好有公开 API 成本；能与其他模型形成一定横向比较。

优先调查 Moonshot/Kimi、OpenAI、Anthropic、Google、DeepSeek、Alibaba/Qwen；可进一步调查 xAI 与智谱 GLM。厂商范围只是检索起点，不构成入选结论。

## 决策程序

1. 建立候选记录，并核验精确名称、版本和发布日期。
2. 统计候选 Benchmark 覆盖，不同设置的不兼容成绩不计作可比覆盖。
3. 核验 API availability、公开价格、工程元数据和来源等级。
4. 评估国内外代表性、厂商分布和场景代表性。
5. 团队评审状态；只有 `final` 状态进入正式模型，不因缺数自行补值。

## 状态

- `pending`：待调查或证据不足。
- `likely`：资料与覆盖初步满足要求，待团队确认。
- `excluded`：不纳入，并记录可复核理由。
- `final`：团队通过数据覆盖和可比性审查后正式纳入。

## 候选模型登记视图

权威数据表为 `data/model_candidates.csv`。下表是 2026-08-16 的 Member A 候选池快照；`likely` 不是最终入选。

| ID | Provider | Model | Version | Release Date | Benchmark Coverage | Pricing Available | Candidate Status | Notes |
|---|---|---|---|---|---|---|---|---|
| kimi-k3 | Moonshot AI | Kimi K3 | kimi-k3 | 2026-07-16 | 17/24 raw | 待 Member B | likely | 题目要求必选；Kimi 官方比较矩阵锚点 |
| gpt-5.6-sol | OpenAI | GPT-5.6 Sol | gpt-5.6-sol | 2026-07-09 | 23/24 raw | 待 Member B | likely | Kimi/OpenAI 两张对照矩阵均覆盖 |
| claude-fable-5 | Anthropic | Claude Fable 5 | claude-fable-5 | 2026-06-09 | 21/24 raw | 待 Member B | likely | fallback 会影响部分评测 |
| claude-opus-4.8 | Anthropic | Claude Opus 4.8 | claude-opus-4.8 | 2026-05-28 | 23/24 raw | 待 Member B | likely | 成熟对照数据较多 |
| gpt-5.5 | OpenAI | GPT-5.5 | gpt-5.5 | 2026-04-23 | 23/24 raw | 待 Member B | likely | 稳定基线 |
| glm-5.2 | Z.ai | GLM-5.2 | GLM-5.2 | 2026-06-16 | 8/24 raw | 待 Member B | likely | 国产开源代表，需补数据 |
| gemini-3.1-pro-preview | Google | Gemini 3.1 Pro Preview | gemini-3.1-pro-preview | 2026-02-19 | 6/24 raw | 待 Member B | likely | Google 代表，仍是 preview |
| deepseek-v4-pro-0813 | DeepSeek | DeepSeek V4 Pro 0813 | DeepSeek V4 Pro 0813 | 2026-08-13 | 1/24 raw | 待 Member B | pending | 发布距截止日仅 4 天，需补 AA 分项与官方版本证据 |
| qwen3.8-2.4t-a95b | Alibaba | Qwen3.8 2.4T A95B | Qwen3.8 2.4T A95B | 2026-08-12 | 1/24 raw | 待 Member B | pending | 发布距截止日仅 5 天，需补 AA 分项与官方版本证据 |

## 尚待数据决定

- DeepSeek 与 Qwen 的截止日前新版本是否因分项覆盖不足移出最终池。
- 最终 6–8 个模型名单及排除理由。
- 数学、代码、多模态、长文本等同类指标采用哪个版本。
- 哪些指标达到 75% 可比覆盖并进入核心体系。
- 是否有足够一致的效率数据进入主模型，还是仅作补充分析。
