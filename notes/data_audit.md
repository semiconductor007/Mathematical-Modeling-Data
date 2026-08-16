# 数据审计报告

## 审计状态

- 审计日期：2026-08-16
- A 第一轮正式审计：已完成
- B 第一轮正式审计：已完成（只读对象 `origin/data-metadata@a57ccff`）
- C staging：已生成，尚未进入正式 raw
- 原则：本文件只报告问题，不直接改写 A/B 原始记录

## A 数据概况

只读审计对象为 `origin/data-benchmark`：

```text
候选模型：9
Benchmark raw：145 行
compatible=false：39 行
official_technical_report：143 行（98.6%）
independent_evaluation：2 行（1.4%）
宽口径重复 model_id + benchmark 组合：12 组
```

### 数据来源偏倚 / source concentration risk

A 当前数据高度集中在模型厂商官方技术报告。论文不得写成“所有 Benchmark 数据均来自独立第三方评测平台”，应准确表述为：

> 公开数据主要来自模型官方技术报告，并辅以少量独立第三方评测。

建议对最终进入核心指标的 Benchmark 尽量补充独立第三方来源进行交叉验证；本轮不通过修改 A 数据来实现。

## 12 组重复组合审计

下表的“重复”仅指相同 `(model_id, benchmark)` 出现两行。经字段级检查，**0 组属于完全相同的重复记录**；12 组全部来自不同来源且 test setting 不同，其中 8 组的 `benchmark_version` 标签也不同。

| 模型 | Benchmark | 数量 | 来源与分数 | version/setting 判断 | 是否可直接混合 | 建议状态 |
|---|---|---:|---|---|---|---|
| Claude Fable 5 | GPQA Diamond | 2 | Kimi 92.6；OpenAI 92.6 | version 标签不同；Kimi 指定 no-tools、temperature/top_p，OpenAI 为 model-appropriate high/max | 否 | 需要修正：按来源 cohort 分开 |
| Claude Opus 4.8 | GPQA Diamond | 2 | Kimi 91；OpenAI 92 | version 和 setting 不同 | 否 | 需要修正：按来源 cohort 分开 |
| GPT-5.5 | GPQA Diamond | 2 | Kimi 93.5；OpenAI 93.6 | version 和 setting 不同 | 否 | 需要修正：按来源 cohort 分开 |
| GPT-5.6 Sol | GPQA Diamond | 2 | Kimi 94.1；OpenAI 94.6 | version 和 setting 不同 | 否 | 需要修正：按来源 cohort 分开 |
| Claude Fable 5 | GDPval-AA v2 | 2 | Kimi snapshot 1747；OpenAI snapshot 1759.6 | 不同 AA snapshot/version 标签和来源 | 否 | 等待更多来源：固定直接 AA 快照后再选 |
| Claude Opus 4.8 | GDPval-AA v2 | 2 | Kimi 1593；OpenAI 1600.1 | 不同 snapshot/version 标签和来源 | 否 | 等待更多来源 |
| GPT-5.5 | GDPval-AA v2 | 2 | Kimi 1491；OpenAI 1493.7 | 不同 snapshot/version 标签和来源 | 否 | 等待更多来源 |
| GPT-5.6 Sol | GDPval-AA v2 | 2 | Kimi 1736；OpenAI 1747.8 | 不同 snapshot/version 标签和来源 | 否 | 等待更多来源 |
| Claude Fable 5 | Terminal-Bench 2.1 | 2 | Kimi 88；OpenAI 83.1 | version 同为 2.1，但均为 model-specific/mixed harness | 否 | 保留但不进入核心数据 |
| Claude Opus 4.8 | Terminal-Bench 2.1 | 2 | Kimi 84.6；OpenAI 78.9 | version 相同，harness/setting 不同 | 否 | 保留但不进入核心数据 |
| GPT-5.5 | Terminal-Bench 2.1 | 2 | Kimi 83.4；OpenAI 85.6 | version 相同，harness/setting 不同 | 否 | 保留但不进入核心数据 |
| GPT-5.6 Sol | Terminal-Bench 2.1 | 2 | Kimi 88.8；OpenAI 88.8 | 分数相同但来源和 harness/setting 不同，仍非完全重复 | 否 | 保留但不进入核心数据 |

分类汇总：

```text
完全重复：0 组
不同来源：12 组
不同 setting：12 组
不同 benchmark_version 标签：8 组
当前可直接进入同一核心队列：0 组
需要修正：4 组（GPQA）
等待更多来源：4 组（GDPval-AA v2）
保留但不进入核心：4 组（Terminal-Bench）
```

“需要修正”不是要求删除行，而是要求覆盖率和后续建模按来源/设置 cohort 分队列。

## 宽口径与严格可比覆盖率

重新计算结果：

```text
按 benchmark 名称统计的最大 raw coverage：7/9 = 77.8%
按 benchmark_version + test_setting + source_name 且 compatible=true 的最佳队列：6/9 = 66.7%
```

GPQA Diamond 和 GDPval-AA v2 的宽口径为 7/9，但严格队列最多 6/9；Terminal-Bench 宽口径为 7/9，但因全部相关记录 `compatible=false`，严格队列为 0/9。

因此覆盖率不能只按 Benchmark 名称计算：

```text
同名 Benchmark ≠ 同版本 ≠ 同测试设置 ≠ 同可比队列
```

在 CRITIC/TOPSIS 数据冻结前，必须使用严格 cohort 覆盖率，不能用同名指标合并制造 75% 覆盖。

## C staging 审计状态

- `results/efficiency_staging.csv` 明确标记 `NOT FOR MODELING / REVIEW ONLY / NOT RAW DATA`。
- 27 行、9 模型、3 指标，均有直接 AA provider URL、HTTP 200、UTC 检索时间和 SHA-256。
- 27 行均为 `manual_review_required=true`、`candidate_compatible=false`；模型配置尚未冻结。
- 正式 `data/raw/cost_efficiency.csv` 与 `data/sources/efficiency_sources.csv` 仍为 0 数据行。

## C efficiency configuration audit

9 个模型均已完成配置级复核，详表见 `results/efficiency_configuration_review.csv`：

| model_id | status | 主要风险/结论 |
|---|---|---|
| `kimi-k3` | CONDITIONAL | Kimi 第一方且三指标同配置；页面没有命名 effort，需团队接受 AA 默认 reasoning 配置 |
| `gpt-5.6-sol` | PASS | max、OpenAI 第一方、版本及三指标配置均明确 |
| `claude-fable-5` | HOLD | 明示 Opus 4.8 Fallback；现有证据不能证明每次均由 Fable 5 执行或分离混合观测 |
| `claude-opus-4.8` | PASS | Adaptive Reasoning、Max Effort、Anthropic 第一方且无 fallback 标签 |
| `gpt-5.5` | PASS | xhigh、OpenAI 第一方；deprecated 是生命周期状态，不使截止日前的可验证数据自动失效 |
| `glm-5.2` | HOLD | Together AI 是第三方；所选项无量化后缀但精度未披露，同页另有 FP4/FP8/NVFP4 部署 |
| `gemini-3.1-pro-preview` | CONDITIONAL | AI Studio 与 Vertex 被 AA 分开统计；需冻结 provider 选择及未命名 reasoning 配置政策 |
| `deepseek-v4-pro-0813` | PASS | 0813 显示名/slug、Reasoning、Max Effort、DeepSeek 第一方均明确 |
| `qwen3.8-2.4t-a95b` | CONDITIONAL | Alibaba Cloud 第一方且只有一个 provider 对象；具体 effort 未显示，不得猜测 |

风险控制结论：

- **Provider**：第一方记录优先；Google 的 AI Studio/Vertex 不合并；Together AI 的 GLM 部署不与第一方 API 自动等同。
- **Reasoning effort**：命名 effort 必须保留；未显示时使用 `NA`，只能以“AA default reasoning configuration”描述。
- **Fallback**：Claude Fable 5 的 fallback 明示且可能改变模型身份，因此不进入 Core A/B。
- **Quantization/deployment**：GLM 同页存在 FP4、FP8、NVFP4 和无后缀部署；无后缀不等于已证明全精度。
- **指标口径**：TTFT 与 TTFA 不互换；E2E 仅为 AA 标准化 500-token 响应时间，不代表任意长度完整回答。
- **滚动窗口**：72 小时 P50 会随 provider 负载和基础设施变化，跨日期抓取值不可当作同一静态测量。
- **日期**：未来正式 raw 对本批记录使用 `measurement_date=NA`、`retrieval_date=2026-08-16`，并保留 rolling-window 设置。

Core Set A 为 4/9（44.4%）；接受三个明确 CONDITIONAL 政策后的最大合理队列为 7/9（77.8%）。该覆盖率不包含两个 HOLD，未为达到 75% 降低审计标准。

## B metadata first-round audit

只读审计对象：`origin/data-metadata@a57ccff`。

```text
model_metadata.csv：8 行
metadata_sources.csv：71 行
retrieval_date：均为 2026-08-16
价格主列口径：列名声明 USD / 1M tokens
```

主要问题：

1. **候选池不一致（阻塞跨表合并）**：A 有 9 个候选，B 有 8 行。按严格 `model_id`，A 中缺少 B 对应行的有 `claude-fable-5`、`claude-opus-4.8`、`gpt-5.5`、`gemini-3.1-pro-preview`、`deepseek-v4-pro-0813`、`qwen3.8-2.4t-a95b`；B 额外/异名为 `claude-opus-4-8`、`gemini-3.1-pro`、`deepseek-v4-pro`、`qwen3.8-max`、`grok-4.6`。
2. **严格版本对齐不足**：只有三个 `model_id` 与 A 直接相同；其中 `kimi-k3` 的 exact_version 为 `Kimi K3`、`gpt-5.6-sol` 为 `GPT-5.6 Sol`，均不与 A 的 slug 型 exact_version 严格相等；仅 `glm-5.2 / GLM-5.2` 严格相等。不能依靠大小写或显示名猜测自动合并。
3. **Qwen 是不同候选**：B 的 `qwen3.8-max` / Qwen3.8-Max 不能替代 A 的 `qwen3.8-2.4t-a95b` / Qwen3.8 2.4T A95B。
4. **价格字段语义**：输入、输出、cached input、batch input/output 均分列，未发现相互代填；但没有 `cache_write_price` 字段，也没有独立 `price_currency`/`price_unit` 字段。单位主要由列名和 notes 表达，后续 schema 冻结时应显式确认。
5. **条件价格不可压成单值**：OpenAI 长上下文价格缺失；Gemini、Grok 有上下文分档；DeepSeek 有峰谷输入/输出价；GLM 是 CNY 原价按 7.10 汇率转 USD。这些条件必须保留，不能只取一个“统一价格”而丢失套餐、地区或时间。
6. **来源直达性**：主表每行只有一个 `source_url`，但部分字段来自二级来源或其他页面；应以 71 行来源表逐字段追踪。Kimi 最大输出、Gemini context、GLM 最大输出等已在 B notes 标记二级来源/冲突，不能在核心模型中默认为已无争议。
7. **API identifier**：schema 没有独立 API endpoint/model identifier 字段；部分 ID 仅写在 exact_version 或 notes，后续若作为工程指标使用需先统一字段政策。
8. **日期**：所有检索日期早于 `DATA_CUTOFF_DATE=2026-08-17`；但若 `publication_date` 实际只是检索时页面状态，不应把它解释为价格首次生效日。`pricing_effective_date` 仍需逐模型保持官方有效日期语义。

本轮只记录问题，未修改 B 的 `model_metadata.csv`、`metadata_sources.csv` 或候选表。

## Validator gap

本轮不修改共享的 `scripts/validate_data.py`，仅记录以下缺口供团队决定：

1. 规则要求缺失值必须为 `NA`，但验证器将空字符串也视为缺失。
2. 未校验 `compatible` 是否只能为规范布尔值。
3. 效率数据的日期格式和截止日期未校验。
4. `cost_efficiency.csv` 没有 `exact_version` 字段，版本只能通过候选外键和 `test_setting/notes` 间接追踪。
5. `main` 候选表仍只有表头；在 A 候选表进入 `main` 前，C 正式 raw 行会因外键不存在而失败。

## 数据冻结意见

- A：尚未通过数据冻结；来源集中、严格覆盖不足和重复 cohort 选择仍需处理。
- B：已有数据，但候选身份、exact_version、价格条件与 schema 字段仍需修正/冻结，尚未通过数据冻结。
- C：staging 采集成功，但配置/provider 未冻结，暂不进入正式 raw。
