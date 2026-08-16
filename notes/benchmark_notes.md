# Benchmark 调研记录（Member A）

## Phase 1 冻结结论

- 最终模型池为 6 个：Kimi K3、GPT-5.6 Sol、Claude Fable 5、Claude Opus 4.8、GPT-5.5、GLM-5.2。
- 冻结 9 个核心指标；严格可比覆盖为 5/6（83.3%）或 6/6（100%），详见 `results/core_indicator_selection.csv`。
- Gemini 3.1 Pro Preview、DeepSeek V4 Pro 0813、Qwen3.8 2.4T A95B 的原始记录继续保留，但不进入 Phase 1 最终模型池。

## 数据截面与成果

- 检索日期：2026-08-16；数据截止：2026-08-17。
- 候选池：9 个模型、8 家厂商；最终冻结 6 个。DeepSeek、Qwen 与 Gemini 因版本状态或严格可比覆盖不足标为 `excluded`，原始记录继续保留。
- 原始成绩：143 条 Kimi/OpenAI 对照记录 + 2 条 Artificial Analysis 综合指数记录，共 145 条。
- 候选指标池：17 个概念指标（工具/无工具和长上下文档位在原始表中拆行），另保留 Artificial Analysis 综合指数作为筛选辅助。
- 所有缺失均为 `NA`；没有插补、图读数或自行调用模型测试。

## 候选版本证据

| 模型 | 发布日期 | 版本证据 |
|---|---:|---|
| Kimi K3 (`kimi-k3`) | 2026-07-16 | [Kimi 官方研究页](https://www.kimi.com/blog/)、[Kimi K3 官方仓库](https://github.com/MoonshotAI/Kimi-K3) |
| GPT-5.6 Sol (`gpt-5.6-sol`) | 2026-07-09 | [OpenAI 官方发布页](https://openai.com/index/gpt-5-6/) |
| Claude Fable 5 | 2026-06-09 | [Anthropic 官方发布页](https://www.anthropic.com/news/claude-fable-5-mythos-5) |
| Claude Opus 4.8 | 2026-05-28 | [Anthropic 官方发布页](https://www.anthropic.com/news/claude-opus-4-8) |
| GPT-5.5 (`gpt-5.5`) | 2026-04-23 | [OpenAI 官方发布页](https://openai.com/index/introducing-gpt-5-5/) |
| GLM-5.2 (`GLM-5.2`) | 2026-06-16 | [Z.ai 官方发布页](https://z.ai/blog/glm-5.2) |
| Gemini 3.1 Pro Preview | 2026-02-19 | [Google 官方模型卡](https://deepmind.google/models/model-cards/gemini-3-1-pro)、[API 型号页](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview) |
| DeepSeek V4 Pro 0813 | 2026-08-13 | [Artificial Analysis 独立模型页](https://artificialanalysis.ai/models/deepseek-v4-pro)；身份核验细节见 `metadata_sources.csv` |
| Qwen3.8 2.4T A95B | 2026-08-12 | [Artificial Analysis 独立模型页](https://artificialanalysis.ai/models/qwen3-8-2-4t-a95b)；身份核验细节见 `metadata_sources.csv` |

## 指标池与当前建议

| 维度 | 候选指标 | 当前处理 |
|---|---|---|
| 高难推理 | GPQA Diamond、HLE-Full | GPQA 暂列核心候选；HLE 需补 Gemini、GLM 和两款截止日前新模型 |
| 数学 | FrontierMath v2 Tier 1–3/Tier 4、MathVision | FrontierMath 为文本数学首选但覆盖不足；MathVision 仅作多模态数学补充 |
| 代码 | SWE-Bench Pro、DeepSWE v1.1、Terminal-Bench 2.1、FrontierSWE、SciCode | SciCode 暂列核心候选；其余因 agent harness 不同先作补充 |
| 专业任务 | GDPval-AA v2、Agents' Last Exam、OfficeQA Pro | GDPval-AA v2 暂列核心候选；其余因模型绑定不同 harness 暂作补充 |
| 多模态 | MMMU-Pro、OmniDocBench、CharXiv RQ | 保留候选，当前可比覆盖不足 75% |
| 长文本 | AA-LCR、GraphWalks BFS 256K/1M、CharXiv RQ | AA-LCR 暂列核心候选；GraphWalks 覆盖低，仅作补充 |

## 可比性规则的实际执行

- `compatible=true` 只表示同一来源、同一版本和同一披露协议下可组成一个队列，不意味着不同厂商的“max/xhigh”消耗相同推理计算量。
- Terminal-Bench、DeepSWE、FrontierSWE、SWE-Bench Pro、Agents' Last Exam、OfficeQA Pro 因 agent harness 随模型变化，统一标记 `compatible=false`，不得进入严格主排名。
- HLE、MMMU-Pro、CharXiv、MathVision 的无工具/有工具成绩分别存储，禁止取两者中较高值后混排。
- 覆盖率脚本已改为按 `benchmark_version + test_setting + source_name` 划分可比队列，避免把同名不同设置合并；同一独立平台的逐模型证据页可以归入同一队列。

## 来源冲突

以下冲突均在原始表并列保留，没有擅自选值：

1. **GPQA Diamond**：Kimi 报告与 OpenAI GPT-5.6 发布页对 GPT-5.6 Sol、GPT-5.5、Claude Opus 4.8 等给出略有差异的成绩。例如 GPT-5.6 Sol 为 94.1 与 94.6。原因可能包括评测快照、推理配置或内部复测差异；两个来源属于不同 cohort。
2. **GDPval-AA v2**：Kimi 报告（Artificial Analysis 2026-07-23 快照）与 OpenAI 发布页的 Elo 不完全相同，例如 GPT-5.6 Sol 为 1736 与 1747.8。Elo 会随榜单池和快照变化，不得混合。
3. **Terminal-Bench 2.1**：两张官方表的分数不同，且明确使用 Kimi Code、Codex、Claude Code、Terminus 2 等不同 harness，全部作为补充数据。

## 覆盖率结论

团队已采用第二条合规路径：将 preview 或距离截止日过近且分项稀疏的 Gemini、DeepSeek、Qwen 移出最终池。覆盖率分母因此按 6 个 `final` 模型计算；9 个冻结指标均达到 75% 门槛，未以插值或跨设置拼接补足覆盖。

## 数据源等级

- Level A：Artificial Analysis 统一评测及官方榜单快照。
- Level B：Agents' Last Exam 等 Benchmark 官方榜单。
- Level C：Kimi K3、GPT-5.6 官方技术/发布报告中的对照表。
- 本批次没有把新闻、自媒体或搜索摘要作为数值来源。
