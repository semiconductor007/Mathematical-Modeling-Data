# Phase 2 清洗与一致性检查记录

状态：**COMPLETED**

## 处理原则

- `data/raw/` 只读，所有转换结果写入 `data/processed/`。
- 最终模型由 `candidate_status=final` 唯一确定，共 6 个。
- 核心能力记录使用 `scripts/phase2_core_cohorts.csv` 固定 benchmark、版本、测试设置和来源队列，不跨快照选高值。
- 数值保持原始单位与精度；空字符串统一阻止进入处理结果，未披露值保存为字面量 `NA`。
- 不插补 5 个缺失核心成绩。后续相关性与综合评价必须显式说明缺失处理策略。
- 效率观测值完整保留；只有 `compatible=true` 的配置复制到 `comparable_*` 字段。Claude Fable 5 和 GLM-5.2 的严格可比效率保持 `NA`。

## 生成物

| 文件 | 内容 | 规模 |
|---|---|---:|
| `data/processed/core_benchmark_matrix.csv` | 最终模型 × 核心能力宽表 | 6 × 9 指标 |
| `data/processed/core_benchmark_long.csv` | 含版本、设置、来源和缺失原因的长表 | 54 行 |
| `data/processed/model_attributes.csv` | 元数据、价格、效率观测值及严格可比值 | 6 行 |
| `data/processed/indicator_quality.csv` | 核心指标覆盖率、单位和缺失模型 | 9 行 |
| `data/processed/phase2_quality_report.csv` | 阶段出口检查 | 8 项 |
| `data/merged/model_dataset.csv` | 最终模型对应全部原始记录的 JSON 保真合并 | 6 行 |

## 可复现命令

```bash
python scripts/process_phase2_data.py
python scripts/merge_data.py --final-only --force
python scripts/validate_data.py
python -m unittest discover -s tests -v
```

## Phase 3 准入与限制

Phase 3 可使用 `core_benchmark_long.csv` 做分布、相关性、覆盖率和共线性分析，并复核 Phase 1 冻结指标。不得直接把不同 `score_unit` 的原值拼接求和；标准化只在建模脚本中进行。含 `NA` 的指标不得静默按零处理，效率滚动观测也不得解释为永久属性。
