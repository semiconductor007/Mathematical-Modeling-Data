"""Question 2 scenario evaluation specified by model(1).md section 3."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from src.q1.analysis import topsis_scores, write_csv

OBJECTIVE_SHARE = 0.5
PERTURBATION_FACTORS = (0.8, 0.9, 1.1, 1.2)
SCENARIO_LABELS = {
    "research_long_text": "科研长文本分析",
    "daily_dialogue": "大众日常通用对话",
    "code_development": "计算机代码开发",
}


def kendall_tau(left: dict[str, int], right: dict[str, int]) -> float:
    concordant = discordant = 0
    models = sorted(left)
    for index, first in enumerate(models):
        for second in models[index + 1 :]:
            product = (left[first] - left[second]) * (right[first] - right[second])
            concordant += int(product > 0)
            discordant += int(product < 0)
    return (concordant - discordant) / (concordant + discordant)


def load_inputs(root: Path) -> dict[str, object]:
    normalized = pd.read_csv(root / "results/q1/normalized_data.csv", encoding="utf-8-sig")
    normalized = normalized.set_index("model_id")
    weights_frame = pd.read_csv(root / "results/q1/critic_weights.csv", encoding="utf-8-sig")
    q1_ranking = pd.read_csv(root / "results/q1/topsis_ranking.csv", encoding="utf-8-sig")
    priorities = pd.read_csv(root / "scripts/phase5_scenario_priorities.csv", encoding="utf-8-sig")
    metrics = weights_frame["metric"].tolist()
    critic = weights_frame.set_index("metric")["weight"].astype(float).to_dict()
    if not math.isclose(sum(critic.values()), 1.0, abs_tol=1e-10):
        raise ValueError("Q1 CRITIC weights do not sum to one")
    if set(priorities["indicator_key"]) != set(metrics):
        raise ValueError("Scenario priority metrics do not match Q1 final metrics")
    for scenario, frame in priorities.groupby("scenario"):
        if len(frame) != len(metrics) or not math.isclose(float(frame["subjective_weight"].sum()), 1.0, abs_tol=1e-10):
            raise ValueError(f"Subjective weights for {scenario} must cover all metrics and sum to one")
    return {
        "normalized": normalized,
        "weights_frame": weights_frame,
        "q1_ranking": q1_ranking,
        "priorities": priorities,
        "metrics": metrics,
        "critic": critic,
    }


def combined_weights(priorities: pd.DataFrame, critic: dict[str, float]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for scenario, group in priorities.groupby("scenario", sort=False):
        for row in group.itertuples():
            objective = critic[row.indicator_key]
            subjective = float(row.subjective_weight)
            combined = OBJECTIVE_SHARE * objective + (1 - OBJECTIVE_SHARE) * subjective
            rows.append({
                "scenario": scenario,
                "scenario_name": SCENARIO_LABELS[scenario],
                "metric": row.indicator_key,
                "critic_weight": objective,
                "subjective_weight": subjective,
                "objective_share": OBJECTIVE_SHARE,
                "combined_weight": combined,
                "weight_change_vs_q1": combined - objective,
                "rationale": row.rationale,
            })
    frame = pd.DataFrame(rows)
    totals = frame.groupby("scenario")["combined_weight"].sum()
    if not np.allclose(totals.to_numpy(), 1.0, atol=1e-10):
        raise AssertionError("Combined scenario weights do not sum to one")
    return frame


def scenario_rankings(
    normalized: pd.DataFrame,
    metrics: list[str],
    weight_frame: pd.DataFrame,
    q1_ranking: pd.DataFrame,
) -> pd.DataFrame:
    names = q1_ranking.set_index("model_id")["model"].to_dict()
    q1_ranks = q1_ranking.set_index("model_id")["rank"].to_dict()
    rows: list[dict[str, object]] = []
    for scenario, group in weight_frame.groupby("scenario", sort=False):
        weights = group.set_index("metric")["combined_weight"].to_dict()
        ranked = topsis_scores(normalized, metrics, weights)
        ranked_by_id = ranked.set_index("model_id").to_dict("index")
        for model_id in normalized.index:
            base = {
                "scenario": scenario,
                "scenario_name": SCENARIO_LABELS[scenario],
                "model_id": model_id,
                "model": names[model_id],
                "q1_rank": q1_ranks.get(model_id, np.nan),
            }
            if model_id in ranked_by_id:
                item = ranked_by_id[model_id]
                base.update(item)
                base["rank_change_vs_q1"] = int(item["rank"] - q1_ranks[model_id])
                base["rank_improvement_vs_q1"] = int(q1_ranks[model_id] - item["rank"])
                base["ranking_status"] = "ranked_complete_case"
            else:
                base.update({
                    "distance_positive": np.nan,
                    "distance_negative": np.nan,
                    "topsis_score": np.nan,
                    "rank": np.nan,
                    "rank_change_vs_q1": np.nan,
                    "rank_improvement_vs_q1": np.nan,
                    "ranking_status": "not_ranked_insufficient_coverage",
                })
            rows.append(base)
    return pd.DataFrame(rows).sort_values(["scenario", "rank", "model_id"], na_position="last").reset_index(drop=True)


def rank_change_analysis(rankings: pd.DataFrame, q1_ranking: pd.DataFrame) -> pd.DataFrame:
    ranked = rankings.loc[rankings["ranking_status"] == "ranked_complete_case"]
    pivot = ranked.pivot(index=["model_id", "model", "q1_rank"], columns="scenario", values="rank").reset_index()
    rows = []
    scenario_keys = list(SCENARIO_LABELS)
    for row in pivot.itertuples(index=False):
        values = {scenario: int(getattr(row, scenario)) for scenario in scenario_keys}
        best_rank, worst_rank = min(values.values()), max(values.values())
        best = "、".join(SCENARIO_LABELS[key] for key, value in values.items() if value == best_rank)
        worst = "、".join(SCENARIO_LABELS[key] for key, value in values.items() if value == worst_rank)
        ranks_all = [int(row.q1_rank), *values.values()]
        rows.append({
            "model_id": row.model_id,
            "model": row.model,
            "q1_rank": int(row.q1_rank),
            "research_rank": values["research_long_text"],
            "dialogue_rank": values["daily_dialogue"],
            "coding_rank": values["code_development"],
            "research_rank_change": values["research_long_text"] - int(row.q1_rank),
            "dialogue_rank_change": values["daily_dialogue"] - int(row.q1_rank),
            "coding_rank_change": values["code_development"] - int(row.q1_rank),
            "best_scenario": best,
            "worst_scenario": worst,
            "rank_range": max(ranks_all) - min(ranks_all),
            "rank_std": float(np.std(ranks_all, ddof=0)),
            "scenario_sensitivity": "场景敏感型" if max(ranks_all) - min(ranks_all) > 0 else "场景稳定型",
        })
    return pd.DataFrame(rows).sort_values(["rank_range", "q1_rank"], ascending=[False, True]).reset_index(drop=True)


def contribution_analysis(
    normalized: pd.DataFrame,
    metrics: list[str],
    weights: pd.DataFrame,
    rankings: pd.DataFrame,
    metric_names: dict[str, str],
) -> pd.DataFrame:
    rows = []
    rank_lookup = rankings.set_index(["scenario", "model_id"])[["topsis_score", "rank"]].to_dict("index")
    for item in weights.itertuples():
        value = float(normalized.loc["kimi-k3", item.metric])
        result = rank_lookup[(item.scenario, "kimi-k3")]
        rows.append({
            "scenario": item.scenario,
            "scenario_name": item.scenario_name,
            "metric": item.metric,
            "indicator": metric_names[item.metric],
            "kimi_normalized_value": value,
            "critic_weight": item.critic_weight,
            "combined_weight": item.combined_weight,
            "weight_change_vs_q1": item.weight_change_vs_q1,
            "weighted_normalized_component": value * item.combined_weight,
            "weight_shift_profile_effect": value * item.weight_change_vs_q1,
            "scenario_score": result["topsis_score"],
            "scenario_rank": result["rank"],
        })
    return pd.DataFrame(rows)


def sensitivity_analysis(
    normalized: pd.DataFrame,
    metrics: list[str],
    critic: dict[str, float],
    priorities: pd.DataFrame,
    baseline: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    baseline_rank = {
        scenario: group.set_index("model_id")["rank"].astype(int).to_dict()
        for scenario, group in baseline.loc[baseline["ranking_status"] == "ranked_complete_case"].groupby("scenario")
    }
    rows = []
    for metric in metrics:
        for factor in PERTURBATION_FACTORS:
            adjusted = dict(critic)
            adjusted[metric] *= factor
            total = sum(adjusted.values())
            adjusted = {key: value / total for key, value in adjusted.items()}
            for scenario, group in priorities.groupby("scenario", sort=False):
                subjective = group.set_index("indicator_key")["subjective_weight"].astype(float).to_dict()
                combined = {
                    key: OBJECTIVE_SHARE * adjusted[key] + (1 - OBJECTIVE_SHARE) * subjective[key]
                    for key in metrics
                }
                ranked = topsis_scores(normalized, metrics, combined)
                ranks = ranked.set_index("model_id")["rank"].astype(int).to_dict()
                tau = kendall_tau(baseline_rank[scenario], ranks)
                for result in ranked.itertuples():
                    rows.append({
                        "scenario": scenario,
                        "scenario_name": SCENARIO_LABELS[scenario],
                        "perturbed_metric": metric,
                        "factor": factor,
                        "model_id": result.model_id,
                        "score": result.topsis_score,
                        "rank": result.rank,
                        "baseline_rank": baseline_rank[scenario][result.model_id],
                        "rank_change": result.rank - baseline_rank[scenario][result.model_id],
                        "kendall_tau_vs_scenario_baseline": tau,
                    })
    detail = pd.DataFrame(rows)
    summary_rows = []
    for (scenario, model_id), group in detail.groupby(["scenario", "model_id"]):
        summary_rows.append({
            "scenario": scenario,
            "scenario_name": SCENARIO_LABELS[scenario],
            "model_id": model_id,
            "baseline_rank": int(group["baseline_rank"].iloc[0]),
            "minimum_rank": int(group["rank"].min()),
            "maximum_rank": int(group["rank"].max()),
            "mean_rank": float(group["rank"].mean()),
            "rank_std": float(group["rank"].std(ddof=0)),
            "top1_probability": float((group["rank"] <= 1).mean()),
            "top3_probability": float((group["rank"] <= 3).mean()),
            "minimum_kendall_tau": float(group["kendall_tau_vs_scenario_baseline"].min()),
            "scenarios": int(len(group)),
        })
    return detail, pd.DataFrame(summary_rows)


def run_analysis(root: Path, output_dir: Path) -> dict[str, object]:
    inputs = load_inputs(root)
    normalized: pd.DataFrame = inputs["normalized"]  # type: ignore[assignment]
    weights_frame: pd.DataFrame = inputs["weights_frame"]  # type: ignore[assignment]
    q1_ranking: pd.DataFrame = inputs["q1_ranking"]  # type: ignore[assignment]
    priorities: pd.DataFrame = inputs["priorities"]  # type: ignore[assignment]
    metrics: list[str] = inputs["metrics"]  # type: ignore[assignment]
    critic: dict[str, float] = inputs["critic"]  # type: ignore[assignment]
    metric_names = weights_frame.set_index("metric")["indicator"].to_dict()
    weights = combined_weights(priorities, critic)
    rankings = scenario_rankings(normalized, metrics, weights, q1_ranking)
    changes = rank_change_analysis(rankings, q1_ranking)
    kimi = contribution_analysis(normalized, metrics, weights, rankings, metric_names)
    sensitivity, stability = sensitivity_analysis(normalized, metrics, critic, priorities, rankings)
    outputs = {
        "scenario_weights.csv": weights,
        "scenario_rankings.csv": rankings,
        "research_ranking.csv": rankings.loc[rankings["scenario"] == "research_long_text"].reset_index(drop=True),
        "dialogue_ranking.csv": rankings.loc[rankings["scenario"] == "daily_dialogue"].reset_index(drop=True),
        "coding_ranking.csv": rankings.loc[rankings["scenario"] == "code_development"].reset_index(drop=True),
        "rank_change_analysis.csv": changes,
        "kimi_k3_scenario_analysis.csv": kimi,
        "scenario_sensitivity.csv": sensitivity,
        "scenario_stability.csv": stability,
    }
    for name, frame in outputs.items():
        write_csv(frame, output_dir / name)
    return {
        **inputs,
        "scenario_weights": weights,
        "scenario_rankings": rankings,
        "rank_changes": changes,
        "kimi": kimi,
        "sensitivity": sensitivity,
        "stability": stability,
        "metric_names": metric_names,
    }
