# 数据规则

## 1. 范围与禁止事项

- `DATA_CUTOFF_DATE = 2026-08-17`，只使用此前已经公开、可获取且可验证的数据。
- 禁止自行调用任何候选大模型进行 Benchmark。
- 禁止估计、推断、插补、随机生成或从图表肉眼读取缺失数值；缺失统一写 `NA`。
- 禁止为“美化”结果直接修改 `data/raw/`；清洗、换算和标准化只发生在 `data/processed/`，并保留转换依据。
- 禁止将搜索摘要、无法追溯的转载/自媒体/营销文或配置不明截图作为核心数据来源。

## 2. 模型与 Benchmark 身份

- 一个 `model_id` 只对应一个提供商、精确模型名称和精确版本；不得把同系列不同版本拼接成同一模型。
- 同名 Benchmark 必须核对版本、pass@1/pass@k、zero/few-shot、CoT、reasoning effort、工具/联网、agent scaffold、temperature、max tokens、多数投票和评价主体。
- 设置不兼容时保留原始记录，设 `compatible=false`，并在 `notes` 写明原因；不得进入同一横向比较。

## 3. 来源优先级与质量等级

1. 同一权威独立第三方平台对多模型的统一横向评测（Level A）。
2. Benchmark 官方榜单或官方统一评测（Level B）。
3. 厂商官方技术报告、模型卡、API 文档或官方博客（Level C）。
4. 可靠但非一手资料（Level D，仅辅助说明，原则上不进入核心模型）。

每个有效数值必须有直接支持该数值的 `source_url` 和 `retrieval_date`。来源表同时记录发布/测量日期、来源类型、可靠性和备注。

## 4. 缺失、冲突与原始值

- 空缺语义统一为 `NA`，不得用 `0`、空字符串或估计值代替。
- 两个来源冲突时均保留并记录来源、版本、条件及可能原因，由团队评审决定采用方式。
- 始终保留原始值、原始单位和测试设置；任何单位转换都应在 processed 层可复现。

## 5. 单位

- API 价格：`USD / 1M tokens`；输入、输出、缓存、批处理、长上下文和峰谷价格分字段记录。
- Context window 与最大输出：`tokens`。
- TTFT、total latency：`seconds`。
- Output speed：`tokens/s`。
- Benchmark 分数：必须填写 `score_unit`，百分数与 0–1 小数不得混用。
- 价格必须记录 `pricing_effective_date`，必要时在备注写定价地区、套餐、上下文区间和缓存条件。

## 6. 修改与审核

- 原始表采用追加式维护；纠错需在提交信息和 notes 中说明原因。
- Member C 原则上只在 `notes/data_audit.md` 报告他人数据问题，不直接改写其原始记录。
- 合并前必须运行校验与覆盖率检查；校验脚本只报告问题，不自动修改数据。
