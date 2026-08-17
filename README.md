# 第一届天津市五校数学建模联赛 B 题项目

本仓库用于完成 B 题“主流大语言模型综合性能评价建模”。项目将基于截至 **2026-08-17** 可公开获取并可验证的资料，构建模型能力、工程属性、API 成本与效率数据集，并在后续阶段开展综合评价、场景化排名和性能—成本分析。

## 当前阶段

**Phase 1–8 已全部完成。** 仓库包含可追溯原始数据、清洗数据、相关性与指标筛选、CRITIC–TOPSIS 通用评价、三类场景排名、性能—成本模型、稳健性分析、图表及完整建模报告。GLM-5.2 因核心成绩覆盖不足未被插补或强行排名。

## 题目目标

1. 从公开、可验证的数据中筛选关键评价指标，建立综合性能评价体系并比较主流模型，重点分析 Kimi K3。
2. 面向科研长文本、大众通用对话和代码开发建立场景化评价模型。
3. 综合性能、API 成本、推理效率与工程因素，形成不同预算下的模型选型策略。

## 三人分工

| 成员 | 主要职责 | 建议分支 |
|---|---|---|
| Member A | 候选模型池、Benchmark 能力矩阵；后续数据处理、CRITIC、TOPSIS 与问题 3 | `data-benchmark` |
| Member B | 模型精确版本、官方元数据、API 可用性与价格；来源整理和论文数据章节 | `data-metadata` |
| Member C | TTFT、吞吐、延迟、长文本/多模态专项数据；全体原始数据审计 | `data-efficiency` |

详细、可验收的任务清单见 [TASKS.md](TASKS.md)。

## Member B 数据交付与验收

Member B 的数据以 Member A 的候选池为唯一身份基准，并在纳入后续合并前接受 Member C 的配置审计。当前 9 个候选模型的 `model_id`、`model_name`、`provider`、`exact_version` 与 `release_date` 已同 [data/model_candidates.csv](data/model_candidates.csv) 对齐；缺失或未能由一手来源确认的字段统一写为 `NA`，不作估算。

- [x] **精确版本与提供商**：逐模型登记精确名称、API/版本标识、发布日期和提供商，Kimi K3 保持在候选池中。
- [x] **官方工程元数据**：登记 context window、最大输出、图像输入、reasoning 支持与 API availability；每个字段的证据见 [data/sources/metadata_sources.csv](data/sources/metadata_sources.csv)。
- [x] **API 价格与条件**：按 **USD / 1M tokens** 登记标准输入/输出、缓存输入、Batch、长上下文和峰谷价格；地区、上下文分档、缓存条件与生效日期写入原始表备注，未披露项为 `NA`。
- [x] **来源整理**：逐字段来源、发布日期、检索日期、来源 URL 与解释性备注见 [data/sources/metadata_sources.csv](data/sources/metadata_sources.csv)；价格历史、汇率换算、来源冲突和字段歧义见 [notes/metadata_notes.md](notes/metadata_notes.md)。
- [x] **论文数据章节**：可直接引用的候选版本、工程元数据、API 价格、来源方法和裁定说明见 [paper/data_chapter_b.md](paper/data_chapter_b.md)。

### 与 A、C 数据的衔接规则

- 与 Member A：仅以完全相同的 `model_id` 合并；不得用同系列、显示名或大小写近似替代精确版本。
- 与 Member C：API 元数据不替代效率测量。效率数据必须保留 provider、reasoning effort、fallback、量化/部署和滚动窗口等配置；状态为 HOLD 的配置不自动进入核心模型。
- 条件价格不得压缩为无条件单值：OpenAI 长上下文、Gemini prompt 长度分档、DeepSeek 峰谷计费，以及 GLM 的人民币原始定价与 USD 换算均保留条件和说明。
- Kimi K3 与 GLM-5.2 最大输出冲突已由第一方 API/模型文档裁定，第三方 33K/262K 口径不再进入冻结数据。GPT-5.6 Sol 长上下文价格已由官方模型页补全；GLM-5.2 官方 HLE 数据以独立 cohort 保存，不与主 cohort 混用。
- 最新逐项缺口分类及“已补录 / 结构性不适用 / 已裁定”清单见 [notes/data_completeness_audit.md](notes/data_completeness_audit.md)。

## 目录

```text
data/
  model_candidates.csv       候选模型登记表
  raw/                       三类原始数据（禁止原地修饰）
  sources/                   数据来源索引
  processed/                 清洗和标准化结果
  merged/                    经校验后的合并结果
scripts/                     覆盖率、校验和合并工具
notes/                       调研记录与审计意见
figures/                     图表输出
results/                     模型结果输出
paper/                       论文材料（含 data_chapter_b.md）
```

## Git 工作流

1. 从 `main` 建立各自建议分支，只主要修改职责范围内的数据文件。
2. 优先提交 CSV，避免多人同时编辑同一个 Excel；原始层与处理层分离。
3. 小批量提交，提交信息说明新增的数据范围与来源。
4. 合并前运行 `python scripts/validate_data.py` 和 `python scripts/check_coverage.py`，由 Member C 将问题记录到 `notes/data_audit.md`。
5. 不覆盖他人的原始数据；冲突数据并列保留并记录差异，交由团队评审。

## 数据规范

- 数据截面：`DATA_CUTOFF_DATE = 2026-08-17`；每条数据记录 `retrieval_date`，价格另记 `pricing_effective_date`。
- 首选同一权威第三方平台的统一横向测评，其次为厂商官方资料，再次为 Benchmark 官方榜单/论文。
- 每个模型必须精确到版本；同名 Benchmark 还须核对版本、提示设置、推理强度、工具/联网、采样与评价类型。
- 每个有效数字必须有支持该数字的 `source_url`。搜索摘要、转载或无法核验的截图不能作为核心数据来源。
- 缺失值统一写 `NA`，不得插补、猜测或从图表肉眼估算。完整规范见 [DATA_RULES.md](DATA_RULES.md)。

## 建模路线

公开数据 → 清洗与一致性检查 → 相关性分析与指标筛选 → CRITIC 客观赋权 → TOPSIS 通用评价 → AHP/组合赋权的场景化评价 → 性能—成本与 Pareto 前沿 → 敏感性和稳健性分析 → 论文整理。路线和阶段门槛见 [PROJECT_PLAN.md](PROJECT_PLAN.md)。

## 基础命令

```bash
python scripts/validate_data.py
python scripts/check_coverage.py
python scripts/process_phase2_data.py
python scripts/merge_data.py --final-only
python scripts/run_pipeline.py
python -m unittest discover -s tests -v
```

全部脚本仅使用 Python 标准库。`run_pipeline.py` 可重建 Phase 2–7 结果和 SVG 图表，并执行跨阶段校验；任何脚本都不会删除 `NA` 或自行补值。完整报告见 `paper/modeling_report.md`。
