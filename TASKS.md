# 团队任务清单

所有检索只纳入 `2026-08-17` 前已公开且可验证的资料。每项“完成”均意味着相应 CSV 已填写来源 URL、检索日期、版本/设置与必要备注，并通过校验脚本。

## Member A — Benchmark 能力数据

- [x] 建立 6–10 个候选模型池：精确到版本，Kimi K3 必须入池，并记录纳入依据与待核验项。
- [x] 收集 GPQA Diamond 与 HLE：记录版本、评价类型、推理/工具设置和可比性，形成模型 × Benchmark 记录。
- [x] 调研数学指标（FrontierMath、AIME、MATH 类）：选择前先比较覆盖率与测试口径，不因缺数而插值。
- [x] 收集代码指标（SWE-bench Verified/Pro、Terminal-Bench）：明确榜单版本、agent scaffold、工具和 pass@k。
- [x] 收集专业任务指标（GDPval/GDPval-AA）及其统一评价口径。
- [x] 收集多模态指标（MMMU/MMMU-Pro）：核对是否确为同版本、同设置。
- [x] 收集可横向比较的长文本理解/检索/问答 Benchmark，避免用 context window 替代能力成绩。
- [x] 运行覆盖率脚本并标注 Coverage <75% 的指标；提出“核心/补充/暂缓”建议，不自行冻结指标。
- [x] 在 `notes/benchmark_notes.md` 记录来源冲突、设置差异和无法比较的原因。

## Member B — 元数据、官方资料与 API 价格

- [x] 对候选池逐一核验精确名称、版本、发布日期与提供商，确保 `model_id` 与 Member A 一致。
- [x] 收集 context window、最大输出长度、图像输入、reasoning 支持和 API availability，并逐字段留源。
- [x] 收集标准 input/output API 价格，统一为 USD/1M tokens，并记录地区和生效日期。
- [x] 收集 cached input、batch input/output、long-context、峰谷价格；不存在或未披露时写 `NA`。
- [x] 将每个元数据字段的证据登记到 `metadata_sources.csv`，优先厂商官方文档/模型卡。
- [x] 核对套餐、区域、上下文长度或缓存条件，避免把有条件价格当作统一标准价格。
- [x] 在 `notes/metadata_notes.md` 记录价格历史、字段歧义和相互冲突的官方页面。
- [x] 运行数据校验并修正自己负责文件中的格式问题，不改写他人的原始数据。

## Member C — 效率、专项数据与审计

- [x] 寻找覆盖多个候选模型的统一第三方 TTFT、输出速度、总延迟/tokens/s 数据，记录平台、日期和设置。
- [x] 补充可统一横向比较的长文本专项效率/能力资料，并区分能力成绩和工程容量。
- [x] 补充多模态专项数据，核验输入模态、评分口径与模型具体版本。
- [x] 审计 Benchmark 的版本、评价类型、prompt、reasoning effort、工具/联网、采样和 agent scaffold。
- [x] 审计模型同名异版、百分数/小数、价格单位、延迟/速度单位和价格时间截面。
- [x] 检查所有 URL 是否直接支持对应数据，标记无效、二手或仅搜索摘要的来源。
- [x] 检查重复指标、重复记录、来源冲突及 Coverage <75% 项，在 `notes/data_audit.md` 报告而非直接改数据。
- [x] 合并前复核三个原始表和来源表，给出“通过/待修正/不进入核心模型”意见。

## Team Review

- [x] 模型名单最终确认：目标 6–8 个，兼顾国内外厂商、覆盖率、价格与可比性。
- [x] 核心指标最终确认：预计 8–12 个，并说明被删指标的覆盖或重复性理由。
- [x] 数据来源完整性审核：每个有效数字都有可验证的原始出处。
- [x] 数据覆盖率审核：确认核心指标原则上达到 75%，例外项有书面理由。
- [x] Benchmark 可比性审核：只有版本和设置兼容的记录进入同一横向比较。
- [x] 数据截面审核：发布日期、检索日期与价格生效日期满足截止规则。

## 今日最先做的三项

### Member A

1. 建立候选模型池并为每个候选登记“待核验的 Benchmark 范围”。
2. 优先收集 GPQA Diamond、HLE 和一个覆盖较广的数学 Benchmark。
3. 运行覆盖率检查，识别最值得继续补齐的模型 × 指标空缺。

### Member B

1. 锁定候选模型精确版本、发布日期与官方模型页。
2. 收集 context/output/vision/reasoning/API availability 等基础元数据。
3. 收集标准 input/output 价格与生效日期，建立逐字段来源索引。

### Member C

1. 确定一个可覆盖多数候选模型的统一效率评测平台及其测试设置。
2. 收集第一批 TTFT、输出速度和总延迟数据并登记来源。
3. 对 A、B 的首批数据做版本、单位、URL 与重复记录审计。
