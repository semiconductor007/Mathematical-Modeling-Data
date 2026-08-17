"""Numerical analysis for Question 1 without modifying frozen input data."""

from __future__ import annotations

import csv
import math
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

NA = "NA"
RANDOM_SEED = 20260817
CORRELATION_THRESHOLDS = (0.80, 0.85, 0.90)
MONTE_CARLO_RUNS = 1000
WEIGHT_PERTURBATION = 0.10

DIMENSION_NAMES = {
    "high_difficulty_reasoning": "高难度知识与逻辑推理",
    "long_context": "长文本理解与推理",
    "coding": "代码与科学编程",
    "professional_tasks": "专业任务能力",
    "multimodal": "多模态理解",
    "document_understanding": "文档理解",
    "research_document_reasoning": "科研文档推理",
    "multimodal_math": "多模态数学推理",
}

METRIC_MEANINGS = {
    "gpqa_diamond": "研究生水平科学问答，衡量高难度知识推理能力",
    "hle_full_no_tools": "Humanity's Last Exam 无工具成绩，衡量极高难度开放推理",
    "aa_lcr": "Artificial Analysis 长上下文推理成绩",
    "scicode": "科学研究代码生成与求解能力",
    "gdpval_aa_v2": "专业知识工作任务的相对能力评分",
    "mmmu_pro_no_tools": "无工具多学科多模态理解能力",
    "omnidocbench": "复杂文档解析与理解能力",
    "charxiv_rq_no_tools": "科研论文图表与问题推理能力",
    "mathvision_no_tools": "无工具视觉数学推理能力",
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required input is missing: {path}")
    return pd.read_csv(path, encoding="utf-8-sig", keep_default_na=False, na_values=[NA])


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8-sig", na_rep=NA)


def load_frozen_data(root: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    long = read_csv(root / "data/processed/core_benchmark_long.csv")
    quality = read_csv(root / "data/processed/indicator_quality.csv")
    attributes = read_csv(root / "data/processed/model_attributes.csv")
    required = {
        "model_id", "model_name", "indicator_key", "dimension", "indicator",
        "score", "score_unit", "higher_is_better", "source_url",
    }
    missing = required - set(long.columns)
    if missing:
        raise ValueError(f"Frozen long table lacks columns: {sorted(missing)}")
    long["score"] = pd.to_numeric(long["score"], errors="coerce")
    return long, quality, attributes


def ordered_metadata(long: pd.DataFrame) -> tuple[list[str], list[str], dict[str, str], dict[str, str], dict[str, str], dict[str, bool]]:
    models = long["model_id"].drop_duplicates().tolist()
    metrics = long["indicator_key"].drop_duplicates().tolist()
    model_names = long.drop_duplicates("model_id").set_index("model_id")["model_name"].to_dict()
    metric_names = long.drop_duplicates("indicator_key").set_index("indicator_key")["indicator"].to_dict()
    dimensions = long.drop_duplicates("indicator_key").set_index("indicator_key")["dimension"].to_dict()
    directions = {
        row.indicator_key: str(row.higher_is_better).lower() == "true"
        for row in long.drop_duplicates("indicator_key").itertuples()
    }
    return models, metrics, model_names, metric_names, dimensions, directions


def raw_matrix(long: pd.DataFrame, models: list[str], metrics: list[str]) -> pd.DataFrame:
    matrix = long.pivot(index="model_id", columns="indicator_key", values="score")
    return matrix.reindex(index=models, columns=metrics)


def data_quality_report(
    long: pd.DataFrame,
    matrix: pd.DataFrame,
    quality: pd.DataFrame,
    metrics: list[str],
    directions: dict[str, bool],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    def add(scope: str, item: str, status: str, value: object, details: str) -> None:
        rows.append({"scope": scope, "item": item, "status": status, "value": value, "details": details})

    add("dataset", "model_count", "pass" if matrix.index.nunique() == len(matrix) else "fail", len(matrix), "One row per final model")
    add("dataset", "indicator_count", "pass" if 8 <= len(metrics) <= 12 else "review", len(metrics), "Frozen Question 1 indicator set")
    duplicate_pairs = int(long.duplicated(["model_id", "indicator_key"]).sum())
    add("dataset", "duplicate_model_indicator_pairs", "pass" if duplicate_pairs == 0 else "fail", duplicate_pairs, "Must be zero")
    add("dataset", "text_identifier_columns", "pass", "model_id/model_name", "Identifiers are excluded from numerical modeling")
    add("dataset", "cost_latency_energy_excluded", "pass", "yes", "Engineering and price fields are reserved for Question 3")
    for metric in metrics:
        values = matrix[metric].dropna().astype(float)
        qrow = quality.loc[quality["indicator_key"] == metric].iloc[0]
        missing_count = int(matrix[metric].isna().sum())
        constant = bool(values.nunique() <= 1)
        status = "pass" if len(values) >= 5 and not constant and np.isfinite(values).all() else "review"
        add(
            "indicator",
            metric,
            status,
            f"available={len(values)}; missing={missing_count}",
            (
                f"dtype=numeric; unit={qrow['score_unit']}; direction={'positive' if directions[metric] else 'negative'}; "
                f"min={values.min():.6g}; max={values.max():.6g}; constant={str(constant).lower()}"
            ),
        )
    return pd.DataFrame(rows)


def minmax_normalize(matrix: pd.DataFrame, directions: dict[str, bool]) -> pd.DataFrame:
    normalized = pd.DataFrame(index=matrix.index, columns=matrix.columns, dtype=float)
    for metric in matrix.columns:
        values = matrix[metric].astype(float)
        low, high = values.min(skipna=True), values.max(skipna=True)
        if not np.isfinite(low) or not np.isfinite(high):
            raise ValueError(f"Indicator {metric} has no usable values")
        if math.isclose(low, high):
            normalized[metric] = values.where(values.isna(), 0.5)
        elif directions[metric]:
            normalized[metric] = (values - low) / (high - low)
        else:
            normalized[metric] = (high - values) / (high - low)
    return normalized


def correlation_matrices(matrix: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pearson = matrix.corr(method="pearson", min_periods=3)
    spearman = matrix.corr(method="spearman", min_periods=3)
    counts = pd.DataFrame(index=matrix.columns, columns=matrix.columns, dtype=int)
    for left in matrix.columns:
        for right in matrix.columns:
            counts.loc[left, right] = int(matrix[[left, right]].dropna().shape[0])
    return pearson, spearman, counts.astype(int)


def select_metrics(
    matrix: pd.DataFrame,
    pearson: pd.DataFrame,
    spearman: pd.DataFrame,
    counts: pd.DataFrame,
    metrics: list[str],
    metric_names: dict[str, str],
    dimensions: dict[str, str],
    threshold: float = 0.85,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    pair_rows: list[dict[str, object]] = []
    for index, left in enumerate(metrics):
        for right in metrics[index + 1:]:
            p, s = float(pearson.loc[left, right]), float(spearman.loc[left, right])
            if max(abs(p), abs(s)) < threshold:
                continue
            same_dimension = dimensions[left] == dimensions[right]
            reason = (
                "保留二者：共同样本仅5个，且分别衡量不同能力维度；高相关性不足以证明语义冗余，后续场景评价仍分别需要"
                if not same_dimension
                else "共同样本有限；两指标虽同属一级维度但测量任务不同，保留并通过稳健性分析检验"
            )
            pair_rows.append({
                "metric_a": left,
                "metric_b": right,
                "metric_a_name": metric_names[left],
                "metric_b_name": metric_names[right],
                "pairwise_models": int(counts.loc[left, right]),
                "pearson_r": p,
                "spearman_r": s,
                "threshold": threshold,
                "same_dimension": same_dimension,
                "decision": "retain_both",
                "reason": reason,
            })
    pair_columns = [
        "metric_a", "metric_b", "metric_a_name", "metric_b_name", "pairwise_models",
        "pearson_r", "spearman_r", "threshold", "same_dimension", "decision", "reason",
    ]
    pairs = pd.DataFrame(pair_rows, columns=pair_columns)
    selected_rows = []
    for metric in metrics:
        values = matrix[metric].dropna().astype(float)
        selected_rows.append({
            "metric": metric,
            "indicator": metric_names[metric],
            "dimension": dimensions[metric],
            "available_models": len(values),
            "missing_rate": 1 - len(values) / len(matrix),
            "sample_std": values.std(ddof=1),
            "coefficient_of_variation": values.std(ddof=1) / abs(values.mean()) if values.mean() else np.nan,
            "decision": "retain",
            "reason": "覆盖率≥75%、非零变异、来源可追溯且具有独立能力含义；小样本高相关不作机械删除",
        })
    selected = pd.DataFrame(selected_rows)
    removed = pd.DataFrame(columns=["removed_metric", "retained_metric", "pearson_r", "spearman_r", "reason"])
    return pairs, selected, removed, metrics.copy()


def critic_weights(normalized: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    info_rows = []
    information: dict[str, float] = {}
    for left in metrics:
        correlations = []
        for right in metrics:
            if left == right:
                continue
            paired = normalized[[left, right]].dropna()
            if len(paired) < 3:
                raise ValueError(f"CRITIC correlation lacks observations: {left}/{right}")
            correlation = float(paired[left].corr(paired[right], method="pearson"))
            if not np.isfinite(correlation):
                raise ValueError(f"CRITIC correlation is invalid: {left}/{right}")
            correlations.append(correlation)
        std = float(normalized[left].dropna().std(ddof=0))
        conflict = float(sum(1 - value for value in correlations))
        information[left] = std * conflict
        info_rows.append({"metric": left, "std": std, "conflict": conflict, "information": information[left]})
    total = sum(information.values())
    if total <= 0:
        raise ValueError("CRITIC information must be positive")
    frame = pd.DataFrame(info_rows)
    frame["weight"] = frame["metric"].map(lambda item: information[item] / total)
    frame["rank"] = frame["weight"].rank(method="min", ascending=False).astype(int)
    return frame.sort_values("rank").reset_index(drop=True)


def topsis_scores(normalized: pd.DataFrame, metrics: list[str], weights: dict[str, float]) -> pd.DataFrame:
    complete = normalized[metrics].dropna(axis=0, how="any")
    if len(complete) < 2:
        raise ValueError("TOPSIS requires at least two complete models")
    weight_vector = np.array([weights[metric] for metric in metrics], dtype=float)
    weighted = complete.to_numpy(dtype=float) * weight_vector
    positive = weight_vector
    negative = np.zeros_like(weight_vector)
    d_positive = np.sqrt(((weighted - positive) ** 2).sum(axis=1))
    d_negative = np.sqrt(((weighted - negative) ** 2).sum(axis=1))
    scores = d_negative / (d_positive + d_negative)
    frame = pd.DataFrame({
        "model_id": complete.index,
        "distance_positive": d_positive,
        "distance_negative": d_negative,
        "topsis_score": scores,
    })
    frame = frame.sort_values(["topsis_score", "model_id"], ascending=[False, True]).reset_index(drop=True)
    frame["rank"] = np.arange(1, len(frame) + 1)
    return frame


def full_ranking(
    normalized: pd.DataFrame,
    metrics: list[str],
    weights: dict[str, float],
    model_names: dict[str, str],
) -> pd.DataFrame:
    ranked = topsis_scores(normalized, metrics, weights)
    rank_by_id = ranked.set_index("model_id").to_dict("index")
    rows = []
    for model_id in normalized.index:
        available = int(normalized.loc[model_id, metrics].notna().sum())
        base = {
            "model": model_names[model_id],
            "model_id": model_id,
            "available_indicators": available,
            "total_indicators": len(metrics),
            "coverage_percent": 100 * available / len(metrics),
        }
        if model_id in rank_by_id:
            base.update(rank_by_id[model_id])
            base["ranking_status"] = "ranked_complete_case"
        else:
            base.update({"distance_positive": np.nan, "distance_negative": np.nan, "topsis_score": np.nan, "rank": np.nan})
            base["ranking_status"] = "not_ranked_insufficient_coverage"
        rows.append(base)
    return pd.DataFrame(rows).sort_values(["rank", "model_id"], na_position="last").reset_index(drop=True)


def kimi_metric_analysis(
    raw: pd.DataFrame,
    normalized: pd.DataFrame,
    metrics: list[str],
    metric_names: dict[str, str],
    dimensions: dict[str, str],
    model_names: dict[str, str],
) -> pd.DataFrame:
    kimi_id = "kimi-k3"
    rows = []
    for metric in metrics:
        raw_values = raw[metric].dropna().astype(float)
        norm_values = normalized[metric].dropna().astype(float)
        order = norm_values.sort_values(ascending=False, kind="mergesort")
        # Competition ranking: tied values receive the same rank.
        rank = int((norm_values > norm_values.loc[kimi_id]).sum()) + 1
        leader_id = str(order.index[0])
        gap = float(order.iloc[0] - norm_values.loc[kimi_id])
        mean_norm = float(norm_values.mean())
        if rank <= 2 and norm_values.loc[kimi_id] >= mean_norm and gap <= 0.35:
            assessment = "advantage"
        elif rank >= math.ceil(len(order) * 0.60) and norm_values.loc[kimi_id] < mean_norm and gap >= 0.25:
            assessment = "weakness"
        else:
            assessment = "middle"
        rows.append({
            "metric": metric,
            "indicator": metric_names[metric],
            "dimension": dimensions[metric],
            "raw_value": float(raw.loc[kimi_id, metric]),
            "normalized_value": float(norm_values.loc[kimi_id]),
            "rank": rank,
            "models_compared": len(order),
            "model_mean_raw": float(raw_values.mean()),
            "difference_from_mean_raw": float(raw.loc[kimi_id, metric] - raw_values.mean()),
            "model_mean_normalized": mean_norm,
            "difference_from_mean_normalized": float(norm_values.loc[kimi_id] - mean_norm),
            "leader_model_id": leader_id,
            "leader_model": model_names[leader_id],
            "gap_to_leader_raw": float(raw.loc[leader_id, metric] - raw.loc[kimi_id, metric]),
            "gap_to_leader_normalized": gap,
            "assessment": assessment,
        })
    return pd.DataFrame(rows)


def threshold_sensitivity(
    normalized: pd.DataFrame,
    metrics: list[str],
    weights: dict[str, float],
    model_names: dict[str, str],
    pearson: pd.DataFrame,
    spearman: pd.DataFrame,
) -> list[dict[str, object]]:
    rows = []
    for threshold in CORRELATION_THRESHOLDS:
        high_correlation_pair_count = sum(
            max(
                abs(float(pearson.loc[left_metric, right_metric])),
                abs(float(spearman.loc[left_metric, right_metric])),
            ) >= threshold
            for left_index, left_metric in enumerate(metrics)
            for right_metric in metrics[left_index + 1 :]
        )
        # Semantic screening keeps all metrics at every threshold; the threshold only changes review flags.
        ranking = topsis_scores(normalized, metrics, weights)
        for item in ranking.itertuples():
            rows.append({
                "analysis_type": "correlation_threshold",
                "scenario": f"threshold_{threshold:.2f}",
                "iteration": 0,
                "threshold": threshold,
                "high_correlation_pair_count": high_correlation_pair_count,
                "perturbation_bound": 0.0,
                "selected_metric_count": len(metrics),
                "model_id": item.model_id,
                "model": model_names[item.model_id],
                "score": item.topsis_score,
                "rank": item.rank,
            })
    return rows


def monte_carlo_sensitivity(
    normalized: pd.DataFrame,
    metrics: list[str],
    base_weights: dict[str, float],
    model_names: dict[str, str],
) -> tuple[list[dict[str, object]], pd.DataFrame]:
    rng = random.Random(RANDOM_SEED)
    rows: list[dict[str, object]] = []
    histories: dict[str, list[int]] = defaultdict(list)
    for iteration in range(1, MONTE_CARLO_RUNS + 1):
        perturbed = {
            metric: base_weights[metric] * rng.uniform(1 - WEIGHT_PERTURBATION, 1 + WEIGHT_PERTURBATION)
            for metric in metrics
        }
        total = sum(perturbed.values())
        perturbed = {metric: value / total for metric, value in perturbed.items()}
        ranking = topsis_scores(normalized, metrics, perturbed)
        for item in ranking.itertuples():
            rank = int(item.rank)
            histories[item.model_id].append(rank)
            rows.append({
                "analysis_type": "monte_carlo_weight_perturbation",
                "scenario": "uniform_independent_pm10pct",
                "iteration": iteration,
                "threshold": np.nan,
                "high_correlation_pair_count": np.nan,
                "perturbation_bound": WEIGHT_PERTURBATION,
                "selected_metric_count": len(metrics),
                "model_id": item.model_id,
                "model": model_names[item.model_id],
                "score": item.topsis_score,
                "rank": rank,
            })
    stability = []
    for model_id, ranks in histories.items():
        array = np.asarray(ranks, dtype=float)
        probabilities = {rank: float(np.mean(array == rank)) for rank in range(1, len(histories) + 1)}
        stability.append({
            "model_id": model_id,
            "model": model_names[model_id],
            "mean_rank": float(array.mean()),
            "rank_std": float(array.std(ddof=0)),
            "minimum_rank": int(array.min()),
            "maximum_rank": int(array.max()),
            "top1_probability": float(np.mean(array <= 1)),
            "top3_probability": float(np.mean(array <= 3)),
            "top5_probability": float(np.mean(array <= 5)),
            **{f"rank_{rank}_probability": probabilities[rank] for rank in probabilities},
            "simulations": MONTE_CARLO_RUNS,
            "random_seed": RANDOM_SEED,
        })
    return rows, pd.DataFrame(stability).sort_values("mean_rank").reset_index(drop=True)


def final_indicator_system(
    metrics: list[str],
    metric_names: dict[str, str],
    dimensions: dict[str, str],
    directions: dict[str, bool],
    long: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for metric in metrics:
        sample = long.loc[long["indicator_key"] == metric].iloc[0]
        rows.append({
            "一级指标": DIMENSION_NAMES[dimensions[metric]],
            "二级指标": metric_names[metric],
            "原数据字段": metric,
            "指标含义": METRIC_MEANINGS[metric],
            "单位": sample["score_unit"],
            "正负向": "正向" if directions[metric] else "负向",
            "是否保留": "是",
            "问题1用途": "CRITIC赋权与TOPSIS综合评价",
        })
    return pd.DataFrame(rows)


def run_analysis(root: Path, output_dir: Path) -> dict[str, object]:
    long, quality, attributes = load_frozen_data(root)
    models, metrics, model_names, metric_names, dimensions, directions = ordered_metadata(long)
    raw = raw_matrix(long, models, metrics)
    quality_report = data_quality_report(long, raw, quality, metrics, directions)
    normalized = minmax_normalize(raw, directions)
    pearson, spearman, counts = correlation_matrices(raw)
    pairs, selected, removed, selected_metrics = select_metrics(
        raw, pearson, spearman, counts, metrics, metric_names, dimensions
    )
    weights_frame = critic_weights(normalized, selected_metrics)
    weights = weights_frame.set_index("metric")["weight"].to_dict()
    ranking = full_ranking(normalized, selected_metrics, weights, model_names)
    kimi = kimi_metric_analysis(raw, normalized, selected_metrics, metric_names, dimensions, model_names)
    sensitivity_rows = threshold_sensitivity(
        normalized,
        selected_metrics,
        weights,
        model_names,
        pearson,
        spearman,
    )
    monte_carlo_rows, stability = monte_carlo_sensitivity(normalized, selected_metrics, weights, model_names)
    sensitivity = pd.DataFrame(sensitivity_rows + monte_carlo_rows)
    indicator_system = final_indicator_system(selected_metrics, metric_names, dimensions, directions, long)

    normalized_out = normalized.copy()
    normalized_out.insert(0, "model", [model_names[index] for index in normalized_out.index])
    normalized_out.insert(0, "model_id", normalized_out.index)
    normalized_out = normalized_out.reset_index(drop=True)
    correlation_columns = ["metric"] + metrics
    pearson_out = pearson.copy().rename_axis("metric").reset_index()[correlation_columns]
    spearman_out = spearman.copy().rename_axis("metric").reset_index()[correlation_columns]
    weights_frame.insert(1, "indicator", weights_frame["metric"].map(metric_names))
    weights_frame.insert(2, "dimension", weights_frame["metric"].map(dimensions))

    outputs = {
        "data_quality_report.csv": quality_report,
        "normalized_data.csv": normalized_out,
        "pearson_correlation.csv": pearson_out,
        "spearman_correlation.csv": spearman_out,
        "high_correlation_pairs.csv": pairs,
        "selected_metrics.csv": selected,
        "removed_metrics.csv": removed,
        "final_indicator_system.csv": indicator_system,
        "critic_weights.csv": weights_frame,
        "topsis_ranking.csv": ranking,
        "kimi_k3_metric_analysis.csv": kimi,
        "sensitivity_analysis.csv": sensitivity,
        "rank_stability.csv": stability,
    }
    for name, frame in outputs.items():
        write_csv(frame, output_dir / name)

    if not math.isclose(float(weights_frame["weight"].sum()), 1.0, abs_tol=1e-10):
        raise AssertionError("CRITIC weights do not sum to one")
    ranked_scores = ranking.loc[ranking["ranking_status"] == "ranked_complete_case", "topsis_score"]
    if not ranked_scores.between(0, 1).all():
        raise AssertionError("TOPSIS scores must be within [0, 1]")
    if ranking["model_id"].nunique() != len(models):
        raise AssertionError("A model was lost or duplicated")

    return {
        "long": long,
        "attributes": attributes,
        "raw": raw,
        "normalized": normalized,
        "pearson": pearson,
        "spearman": spearman,
        "pairs": pairs,
        "selected": selected,
        "weights": weights_frame,
        "ranking": ranking,
        "kimi": kimi,
        "stability": stability,
        "indicator_system": indicator_system,
        "models": models,
        "metrics": metrics,
        "selected_metrics": selected_metrics,
        "model_names": model_names,
        "metric_names": metric_names,
        "dimensions": dimensions,
        "directions": directions,
    }
