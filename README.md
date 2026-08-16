# 第一届天津市五校数学建模联赛 B 题项目

本仓库用于完成 B 题“主流大语言模型综合性能评价建模”。项目将基于截至 **2026-08-17** 可公开获取并可验证的资料，构建模型能力、工程属性、API 成本与效率数据集，并在后续阶段开展综合评价、场景化排名和性能—成本分析。

## 当前阶段

**Phase 1：模型筛选与数据收集已完成。** 已从 9 个候选模型中冻结 6 个最终模型，并冻结 9 个核心能力指标；三类原始数据、逐字段来源、覆盖率结果和数据审计均已入库。下一阶段为 Phase 2 清洗与一致性检查；尚未执行 CRITIC、TOPSIS 或排名建模。

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
paper/                       论文材料
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

## 后续建模路线

公开数据 → 清洗与一致性检查 → 相关性分析与指标筛选 → CRITIC 客观赋权 → TOPSIS 通用评价 → AHP/组合赋权的场景化评价 → 性能—成本与 Pareto 前沿 → 敏感性和稳健性分析 → 论文整理。路线和阶段门槛见 [PROJECT_PLAN.md](PROJECT_PLAN.md)。

## 基础命令

```bash
python scripts/validate_data.py
python scripts/check_coverage.py
python scripts/merge_data.py
```

三份脚本均使用 Python 标准库，且在只有表头、没有数据时安全运行。合并脚本不会删除 `NA` 或自行补值。
