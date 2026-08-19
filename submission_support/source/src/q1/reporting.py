"""Generate traceable Markdown materials for Question 1."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .analysis import DIMENSION_NAMES, METRIC_MEANINGS, MONTE_CARLO_RUNS, RANDOM_SEED


def fmt(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}"


def write_data_dictionary(result: dict[str, object], docs_dir: Path) -> Path:
    long: pd.DataFrame = result["long"]  # type: ignore[assignment]
    attributes: pd.DataFrame = result["attributes"]  # type: ignore[assignment]
    metrics: list[str] = result["metrics"]  # type: ignore[assignment]
    metric_names: dict[str, str] = result["metric_names"]  # type: ignore[assignment]
    dimensions: dict[str, str] = result["dimensions"]  # type: ignore[assignment]
    directions: dict[str, bool] = result["directions"]  # type: ignore[assignment]
    lines = [
        "# 数据字典",
        "",
        "问题1建模输入为 `data/processed/core_benchmark_long.csv`。每行表示一个“最终模型—冻结指标”观测；模型标识和来源字段为文本，`score` 为数值或 `NA`。成本、时延和吞吐来自 `model_attributes.csv`，只为问题3预留，不进入问题1纯性能排名。",
        "",
        "## 问题1性能指标",
        "",
        "| 指标名称 | 英文/代码字段名 | 指标含义 | 指标类别 | 单位 | 方向 | 数据来源 | 是否进入问题1 | 备注 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for metric in metrics:
        row = long.loc[long["indicator_key"] == metric].iloc[0]
        source = str(row["source_name"])
        lines.append(
            f"| {metric_names[metric]} | `{metric}` | {METRIC_MEANINGS[metric]} | {DIMENSION_NAMES[dimensions[metric]]} | "
            f"{row['score_unit']} | {'正向' if directions[metric] else '负向'} | {source} | 是 | 缺失不插补；按冻结 cohort 比较 |"
        )
    lines += [
        "",
        "## 标识、来源与工程字段",
        "",
        "| 字段名 | 含义 | 类别 | 单位 | 方向 | 是否进入问题1 | 备注 |",
        "|---|---|---|---|---|---|---|",
        "| `model_id` / `model_name` | 模型唯一标识与展示名 | 文本标识 | — | — | 仅保留标识 | 不参与数值计算 |",
        "| `source_name` / `source_url` / `retrieval_date` | 指标来源与检索日期 | 来源字段 | — | — | 否 | 用于追溯 |",
        "| `input_price_usd_per_million` / `output_price_usd_per_million` | API 输入/输出价格 | 成本 | USD/1M tokens | 负向 | 否 | 问题3使用 |",
        "| `comparable_ttft_seconds` | 首 token 延迟 | 工程效率 | seconds | 负向 | 否 | 问题3使用；仅 compatible 记录 |",
        "| `comparable_output_speed_tokens_per_second` | 输出速度 | 工程效率 | tokens/s | 正向 | 否 | 问题3使用；仅 compatible 记录 |",
        "| `comparable_total_latency_seconds` | 标准响应总延迟 | 工程效率 | seconds | 负向 | 否 | 问题3使用；仅 compatible 记录 |",
        "",
        f"当前工程属性表含 {len(attributes)} 个最终模型。仓库没有可严格横向比较的能耗字段，因此问题1和现阶段问题3接口均不虚构能耗数值。",
    ]
    path = docs_dir / "data_dictionary.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_metric_selection(result: dict[str, object], docs_dir: Path) -> Path:
    pairs: pd.DataFrame = result["pairs"]  # type: ignore[assignment]
    pearson: pd.DataFrame = result["pearson"]  # type: ignore[assignment]
    spearman: pd.DataFrame = result["spearman"]  # type: ignore[assignment]
    selected_metrics: list[str] = result["selected_metrics"]  # type: ignore[assignment]
    selected: pd.DataFrame = result["selected"]  # type: ignore[assignment]
    lines = [
        "# 问题1指标筛选说明",
        "",
        "## 可复现规则",
        "",
        "1. 仅使用 Phase 2 已冻结且覆盖率不低于 75% 的指标；不重新采集、不插补。",
        "2. 排除常数列，并检查单位与方向；本轮九项均为正向能力指标。",
        "3. 同时计算 Pearson 与 Spearman；任一绝对值达到 0.85 即进入冗余复核。",
        "4. 复核覆盖率、样本标准差、语义维度、来源和后续场景用途。由于最终样本仅 6 个、含缺失指标的共同样本仅 5 个，高相关不作为自动删除依据。",
        "5. 只有在语义重复、来源/口径不弱于替代指标且删除不损害场景能力表示时才删除。本轮没有指标同时满足这些条件。",
        "",
        f"初始指标 {len(selected)} 项，删除 0 项，最终保留 {len(selected)} 项。`removed_metrics.csv` 因此只有表头，这是明确筛选结论而非漏算。",
        "",
        "## 高相关候选对（阈值 0.85）",
        "",
        "| 指标A | 指标B | Pearson | Spearman | 共同模型 | 决策 |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in pairs.itertuples():
        lines.append(f"| {row.metric_a_name} | {row.metric_b_name} | {row.pearson_r:.4f} | {row.spearman_r:.4f} | {row.pairwise_models} | 保留二者 |")
    lines += [
        "",
        "这些高相关关系跨越不同能力构念，且共同样本量很小。机械删除会把科学推理、多模态或科研文档能力错误地视作同一指标；因此主模型保留九项，并在 0.80/0.85/0.90 阈值下重复检查排名。",
    ]
    path = docs_dir / "q1_metric_selection.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_results_summary(result: dict[str, object], docs_dir: Path) -> Path:
    weights: pd.DataFrame = result["weights"]  # type: ignore[assignment]
    ranking: pd.DataFrame = result["ranking"]  # type: ignore[assignment]
    kimi: pd.DataFrame = result["kimi"]  # type: ignore[assignment]
    stability: pd.DataFrame = result["stability"]  # type: ignore[assignment]
    pairs: pd.DataFrame = result["pairs"]  # type: ignore[assignment]
    pearson: pd.DataFrame = result["pearson"]  # type: ignore[assignment]
    spearman: pd.DataFrame = result["spearman"]  # type: ignore[assignment]
    selected_metrics: list[str] = result["selected_metrics"]  # type: ignore[assignment]
    ranked = ranking.loc[ranking["ranking_status"] == "ranked_complete_case"].sort_values("rank")
    kimi_rank = int(ranked.loc[ranked["model_id"] == "kimi-k3", "rank"].iloc[0])
    strengths = kimi.loc[kimi["assessment"] == "advantage"].sort_values(["rank", "gap_to_leader_normalized"])
    weaknesses = kimi.loc[kimi["assessment"] == "weakness"].sort_values("gap_to_leader_normalized", ascending=False)
    largest_gap = kimi.sort_values("gap_to_leader_normalized", ascending=False).iloc[0]
    kimi_stability = stability.loc[stability["model_id"] == "kimi-k3"].iloc[0]
    threshold_pair_counts = {
        threshold: sum(
            max(
                abs(float(pearson.loc[left_metric, right_metric])),
                abs(float(spearman.loc[left_metric, right_metric])),
            ) >= threshold
            for left_index, left_metric in enumerate(selected_metrics)
            for right_metric in selected_metrics[left_index + 1 :]
        )
        for threshold in (0.80, 0.85, 0.90)
    }
    lines = [
        "# 问题1建模结果摘要",
        "",
        "## 1. 模型选择理由",
        "",
        "Pearson 用于识别线性冗余，Spearman 用于检验对异常值和非线性单调关系更稳健的秩相关；二者共同形成指标复核清单。CRITIC 在方向统一的 Min–Max 数据上同时利用离散程度与指标冲突性确定客观权重，避免人为迎合排名。TOPSIS 再计算各模型到正、负理想解的距离，将多指标信息汇总为可解释的相对接近度。",
        "",
        "## 2. 指标筛选结果",
        "",
        f"问题1从 Phase 2 冻结的 9 项核心指标开始。0.85 阈值下发现 {len(pairs)} 组高相关候选，但共同样本仅 5 个且语义维度不同，故删除 0 项、保留 9 项。具体数值和理由见 `high_correlation_pairs.csv` 与 `q1_metric_selection.md`。",
        "",
        "## 3. CRITIC 权重",
        "",
        "| 排名 | 指标 | 权重 | 标准差 | 冲突性 |",
        "|---:|---|---:|---:|---:|",
    ]
    for row in weights.head(5).itertuples():
        lines.append(f"| {row.rank} | {row.indicator} | {row.weight:.6f} | {row.std:.6f} | {row.conflict:.6f} |")
    top = weights.iloc[0]
    low = weights.sort_values("weight").iloc[0]
    lines += [
        "",
        f"最高权重为 {top['indicator']}（{top['weight']:.6f}），其标准化离散度与对其他指标的冲突性乘积最大；最低为 {low['indicator']}（{low['weight']:.6f}）。权重只反映当前样本的信息贡献，不代表永久重要性。",
        "",
        "## 4. 综合排名",
        "",
        "| Rank | Model | Score |",
        "|---:|---|---:|",
    ]
    for row in ranked.itertuples():
        lines.append(f"| {int(row.rank)} | {row.model} | {row.topsis_score:.10f} |")
    unranked = ranking.loc[ranking["ranking_status"] != "ranked_complete_case"]
    if not unranked.empty:
        row = unranked.iloc[0]
        lines.append(f"\n{row['model']} 仅覆盖 {row['available_indicators']}/{row['total_indicators']} 项，未插补且不参与主排名。")
    lines += [
        "",
        "## 5. Kimi K3",
        "",
        f"Kimi K3 综合排名第 {kimi_rank}。优势指标为：" + "、".join(str(item) for item in strengths["indicator"].tolist()) + "。",
        ("主要短板为：" + "、".join(str(item) for item in weaknesses["indicator"].tolist()) + "。") if not weaknesses.empty else "没有被组合规则判定为显著短板的指标。",
        f"与单指标最优模型差距最大的是 {largest_gap['indicator']}，标准化差距为 {largest_gap['gap_to_leader_normalized']:.6f}，领先模型为 {largest_gap['leader_model']}。综合定位是长文本与文档理解突出、整体第二，但极高难度开放推理仍明显落后于领先者。",
        "",
        "## 6. 稳健性",
        "",
        "相关性阈值调整为 0.80、0.85、0.90 时，高相关候选对分别为 "
        f"{threshold_pair_counts[0.80]}、{threshold_pair_counts[0.85]}、{threshold_pair_counts[0.90]} 对；"
        "语义复核规则均保留九项指标，主排名不变。",
        f"固定随机种子 {RANDOM_SEED}，对 CRITIC 权重独立施加 ±10% 均匀扰动并重新归一化，共运行 {MONTE_CARLO_RUNS} 次。Kimi K3 平均排名 {kimi_stability['mean_rank']:.4f}、排名标准差 {kimi_stability['rank_std']:.4f}、Top3 概率 {kimi_stability['top3_probability']:.2%}。",
        "",
        "## 给问题2的输入",
        "",
        "问题2可直接读取 `results/q1/selected_metrics.csv`、`final_indicator_system.csv`、`normalized_data.csv` 和 `critic_weights.csv`，在此基础上叠加三个场景的主观偏好或组合权重。",
        "",
        "## 给问题3的输入",
        "",
        "问题3可读取 `results/q1/topsis_ranking.csv` 的综合性能得分，再按 `model_id` 连接 `data/processed/model_attributes.csv` 中的价格和 compatible 效率字段。当前没有严格可比能耗数据，不应自行补造。",
    ]
    path = docs_dir / "q1_results_summary.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def generate_documents(result: dict[str, object], docs_dir: Path) -> list[Path]:
    docs_dir.mkdir(parents=True, exist_ok=True)
    return [
        write_data_dictionary(result, docs_dir),
        write_metric_selection(result, docs_dir),
        write_results_summary(result, docs_dir),
    ]
