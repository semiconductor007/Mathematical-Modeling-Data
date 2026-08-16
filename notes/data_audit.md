# Phase 1 数据冻结审计

审计日期：2026-08-17
结论：**PASSED — 准予进入 Phase 2**

## 交付范围

| 数据集 | 记录数 | 来源记录 | 审计结果 |
|---|---:|---:|---|
| 候选模型 | 9（6 final、3 excluded） | 元数据身份来源索引 | 通过 |
| Benchmark | 145 | 30 | 通过；冲突队列并列保留 |
| 元数据与价格 | 9 | 79 | 通过；逐字段留源 |
| 效率 | 9（由 27 条 staging 记录提升） | 27 | 通过；逐指标留源 |

所有表统一使用 `model_id` 关联；有效数字均有直接来源 URL 和检索日期。缺失、未披露或不适用字段写为 `NA`，没有插值、图读数或自行调用模型测试。

## 模型与指标冻结

最终模型：`kimi-k3`、`gpt-5.6-sol`、`claude-fable-5`、`claude-opus-4.8`、`gpt-5.5`、`glm-5.2`。

排除记录继续保留：Gemini 3.1 Pro Preview 因 preview 状态及严格可比覆盖不足；DeepSeek V4 Pro 0813 与 Qwen3.8 2.4T A95B 分别仅在截止日前 4 天、5 天公开，分项覆盖不足。

冻结 9 个核心指标：GPQA Diamond、HLE-Full（no tools）、AA-LCR、SciCode、GDPval-AA v2、MMMU-Pro（no tools）、OmniDocBench、CharXiv RQ（no tools）、MathVision（no tools）。最佳严格可比队列覆盖为 5/6（83.3%）或 6/6（100%），逐项决定见 `results/core_indicator_selection.csv`。

## 可比性与冲突处理

- Benchmark 按 `benchmark_version + test_setting + source_name` 分队列；工具/无工具、推理配置、agent harness 不同的成绩不混排。
- Kimi 与 OpenAI 报告中 GPQA、GDPval-AA 等快照差异并列保留，不选择性取高值。
- 依赖不同 agent scaffold 的 Terminal-Bench、DeepSWE、FrontierSWE、SWE-Bench Pro、Agents' Last Exam、OfficeQA Pro 不进入核心指标。
- 效率统一为 Artificial Analysis 默认约 10k input tokens、single prompt、滚动 72 小时 P50；E2E 是标准化 500-token response。
- Kimi 的未命名配置只称为 “AA default reasoning configuration”。Claude Fable 5 因 Opus fallback、GLM-5.2 因第三方部署与量化未知标为 `compatible=false`，不得进入严格效率横向队列。

## 时间截面与元数据说明

- 数据截止日为 2026-08-17；模型发布日期、检索日期和已填写的价格生效日期均未越界。
- 标准价格统一为 USD/1M tokens；条件价格单列，未披露的 batch、long-context 或峰谷价格不作推断。
- 滚动效率测量没有唯一单日日期，因此 `measurement_date=NA`，检索日期保留为 2026-08-16。
- 原始层保留完整精度；单位换算、舍入与缺失处理留到 Phase 2。

## 自动校验

冻结提交前执行：数据结构与语义校验、最终池覆盖率重算、效率采集器 dry-run、单元测试、合并脚本 smoke test、`git diff --check`。最终结果以提交前命令输出为准；任何失败均阻止推送 `main`。

## 后续建模限制

- 对存在多个权威快照的 Benchmark，Phase 2 必须固定 cohort 后再建模。
- 效率是滚动观测，不能解释为永久稳定的模型属性。
- `compatible=false` 的效率记录只用于个案或局限分析。
- processed 与 merged 层已由 Phase 2 脚本生成；后续模型只读取经校验的冻结 cohort。
