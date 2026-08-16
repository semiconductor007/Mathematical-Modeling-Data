# 数据审计报告

## 审计状态

- 审计日期：2026-08-16
- A 第一轮正式审计：已完成
- B：远程已建立 `data-metadata`，但仍指向 `main` 初始提交，暂无数据可审计
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

## B 状态

本轮 Git fetch 遇到临时网络超时，随后通过 GitHub 官方只读分支 API 确认 `data-metadata` 已建立，但它当前仍指向与 `main` 相同的初始提交 `bc4f13c`。因此 `model_metadata.csv` 和 `metadata_sources.csv` 仍只有表头：

```text
B branch exists; data not available for audit yet
```

未猜测或代填 B 的模型版本、API availability、价格或来源。

## Validator gap

本轮不修改共享的 `scripts/validate_data.py`，仅记录以下缺口供团队决定：

1. 规则要求缺失值必须为 `NA`，但验证器将空字符串也视为缺失。
2. 未校验 `compatible` 是否只能为规范布尔值。
3. 效率数据的日期格式和截止日期未校验。
4. `cost_efficiency.csv` 没有 `exact_version` 字段，版本只能通过候选外键和 `test_setting/notes` 间接追踪。
5. `main` 候选表仍只有表头；在 A 候选表进入 `main` 前，C 正式 raw 行会因外键不存在而失败。

## 数据冻结意见

- A：尚未通过数据冻结；来源集中、严格覆盖不足和重复 cohort 选择仍需处理。
- B：尚无数据可审计。
- C：staging 采集成功，但配置/provider 未冻结，暂不进入正式 raw。
