"""Question 3 models specified by model(1).md section 4."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from src.q1.analysis import topsis_scores, write_csv

INPUT_MILLION_TOKENS = 1.0
OUTPUT_MILLION_TOKENS = 0.2
BUDGETS = (6.0, 10.0, 12.0, 16.0, 20.0)
PERTURBATION_FACTORS = (0.8, 0.9, 1.1, 1.2)


def benefit_minmax(series: pd.Series, higher_is_better: bool) -> pd.Series:
    minimum, maximum = float(series.min()), float(series.max())
    if math.isclose(minimum, maximum):
        raise ValueError(f"Cannot normalize constant engineering field {series.name}")
    if higher_is_better:
        return (series - minimum) / (maximum - minimum)
    return (maximum - series) / (maximum - minimum)


def pareto_table(performance_cost: pd.DataFrame) -> pd.DataFrame:
    included = performance_cost.loc[performance_cost["analysis_status"] == "included_ranked_model"].copy()
    rows = []
    for item in included.itertuples():
        dominators = included.loc[
            (included["model_id"] != item.model_id)
            & (included["standard_workload_cost_usd"] <= item.standard_workload_cost_usd)
            & (included["q1_performance_score"] >= item.q1_performance_score)
            & (
                (included["standard_workload_cost_usd"] < item.standard_workload_cost_usd)
                | (included["q1_performance_score"] > item.q1_performance_score)
            )
        ]
        rows.append({
            "model_id": item.model_id,
            "model": item.model,
            "q1_performance_score": item.q1_performance_score,
            "standard_workload_cost_usd": item.standard_workload_cost_usd,
            "pareto_status": "frontier" if dominators.empty else "dominated",
            "is_pareto_frontier": dominators.empty,
            "dominated_by_model_ids": "" if dominators.empty else ";".join(dominators["model_id"]),
            "dominated_by_models": "" if dominators.empty else "；".join(dominators["model"]),
        })
    return pd.DataFrame(rows).sort_values(["standard_workload_cost_usd", "q1_performance_score"], ascending=[True, False])


def cost_audit(attributes: pd.DataFrame, q1: pd.DataFrame) -> pd.DataFrame:
    q1_status = q1.set_index("model_id")["ranking_status"].to_dict()
    rows = []
    for item in attributes.itertuples():
        has_prices = pd.notna(item.input_price_usd_per_million) and pd.notna(item.output_price_usd_per_million)
        cost = (
            float(item.input_price_usd_per_million) * INPUT_MILLION_TOKENS
            + float(item.output_price_usd_per_million) * OUTPUT_MILLION_TOKENS
            if has_prices else np.nan
        )
        rows.append({
            "model_id": item.model_id,
            "model": item.model_name,
            "input_price_usd_per_million": item.input_price_usd_per_million,
            "output_price_usd_per_million": item.output_price_usd_per_million,
            "price_unit": "USD / 1M tokens",
            "workload_input_million_tokens": INPUT_MILLION_TOKENS,
            "workload_output_million_tokens": OUTPUT_MILLION_TOKENS,
            "standard_workload_cost_usd": cost,
            "price_data_complete": has_prices,
            "efficiency_compatible": bool(item.efficiency_compatible),
            "comparable_ttft_seconds": item.comparable_ttft_seconds,
            "comparable_output_speed_tokens_per_second": item.comparable_output_speed_tokens_per_second,
            "comparable_total_latency_seconds": item.comparable_total_latency_seconds,
            "energy_data_available": False,
            "q1_ranking_status": q1_status[item.model_id],
            "q3_cost_analysis_status": "included" if has_prices else "excluded_missing_price",
            "notes": "能耗字段不存在；不估算。效率仅在 compatible=true 时横向比较。",
        })
    return pd.DataFrame(rows)


def performance_cost_table(audit: pd.DataFrame, q1: pd.DataFrame) -> pd.DataFrame:
    q1_columns = q1[["model_id", "topsis_score", "rank", "ranking_status"]].rename(
        columns={"topsis_score": "q1_performance_score", "rank": "q1_rank"}
    )
    frame = audit[["model_id", "model", "standard_workload_cost_usd"]].merge(q1_columns, on="model_id", how="left")
    frame["analysis_status"] = np.where(
        frame["ranking_status"] == "ranked_complete_case",
        "included_ranked_model",
        "excluded_insufficient_q1_coverage",
    )
    included = frame["analysis_status"] == "included_ranked_model"
    frame.loc[included, "performance_per_usd"] = (
        frame.loc[included, "q1_performance_score"] / frame.loc[included, "standard_workload_cost_usd"]
    )
    frame.loc[included, "cost_rank_among_ranked"] = frame.loc[included, "standard_workload_cost_usd"].rank(method="min").astype(int)
    frame.loc[included, "value_rank_among_ranked"] = frame.loc[included, "performance_per_usd"].rank(method="min", ascending=False).astype(int)
    costs = frame.loc[included, "standard_workload_cost_usd"]
    frame.loc[included, "cost_benefit_index"] = (costs.max() - costs) / (costs.max() - costs.min())
    return frame


def budget_selection(performance_cost: pd.DataFrame) -> pd.DataFrame:
    included = performance_cost.loc[performance_cost["analysis_status"] == "included_ranked_model"]
    rows = []
    for budget in BUDGETS:
        feasible = included.loc[included["standard_workload_cost_usd"] <= budget]
        if feasible.empty:
            rows.append({"budget_level": budget, "budget_limit_usd": budget, "feasible_models": 0})
            continue
        winner = feasible.sort_values(["q1_performance_score", "standard_workload_cost_usd"], ascending=[False, True]).iloc[0]
        rows.append({
            "budget_level": budget,
            "budget_limit_usd": budget,
            "feasible_models": len(feasible),
            "recommended_model_id": winner["model_id"],
            "recommended_model": winner["model"],
            "performance": winner["q1_performance_score"],
            "cost_usd": winner["standard_workload_cost_usd"],
            "unused_budget_usd": budget - winner["standard_workload_cost_usd"],
            "selection_rule": "预算内Q1 TOPSIS得分最高；不含Q1未排名模型",
        })
    return pd.DataFrame(rows)


def regression(performance_cost: pd.DataFrame) -> pd.DataFrame:
    frame = performance_cost.loc[performance_cost["analysis_status"] == "included_ranked_model"].copy()
    x = np.log(frame["standard_workload_cost_usd"].to_numpy(float))
    y = frame["q1_performance_score"].to_numpy(float)
    design = np.column_stack([np.ones(len(x)), x])
    beta = np.linalg.lstsq(design, y, rcond=None)[0]
    fitted = design @ beta
    residuals = y - fitted
    sse = float(np.sum(residuals**2))
    sst = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1 - sse / sst
    adjusted = 1 - (1 - r_squared) * (len(y) - 1) / (len(y) - 2)
    rmse = math.sqrt(sse / len(y))
    frame["ln_cost"] = x
    frame["fitted_performance"] = fitted
    frame["residual"] = residuals
    frame["intercept"] = beta[0]
    frame["slope_log_cost"] = beta[1]
    frame["r_squared"] = r_squared
    frame["adjusted_r_squared"] = adjusted
    frame["rmse"] = rmse
    frame["sample_size"] = len(y)
    frame["model_formula"] = "S = beta0 + beta1 * ln(Cost)"
    frame["inference_scope"] = "exploratory_description_only_n_equals_5"
    return frame[[
        "model_id", "model", "standard_workload_cost_usd", "q1_performance_score", "ln_cost",
        "fitted_performance", "residual", "intercept", "slope_log_cost", "r_squared",
        "adjusted_r_squared", "rmse", "sample_size", "model_formula", "inference_scope",
    ]]


def engineering_efficiency(attributes: pd.DataFrame, q1: pd.DataFrame) -> pd.DataFrame:
    performance = q1.set_index("model_id")["topsis_score"].to_dict()
    compatible = attributes.loc[
        attributes["efficiency_compatible"]
        & attributes["model_id"].map(lambda key: pd.notna(performance[key]))
    ].copy()
    compatible["ttft_benefit_score"] = benefit_minmax(compatible["comparable_ttft_seconds"], False)
    compatible["speed_benefit_score"] = benefit_minmax(compatible["comparable_output_speed_tokens_per_second"], True)
    compatible["latency_benefit_score"] = benefit_minmax(compatible["comparable_total_latency_seconds"], False)
    compatible["engineering_efficiency_score"] = compatible[
        ["ttft_benefit_score", "speed_benefit_score", "latency_benefit_score"]
    ].mean(axis=1)
    compatible["q1_performance_score"] = compatible["model_id"].map(performance)
    compatible["deployment_score"] = 0.7 * compatible["q1_performance_score"] + 0.3 * compatible["engineering_efficiency_score"]
    compatible["efficiency_rank"] = compatible["engineering_efficiency_score"].rank(method="min", ascending=False).astype(int)
    compatible["deployment_rank"] = compatible["deployment_score"].rank(method="min", ascending=False).astype(int)
    compatible["analysis_status"] = "included_compatible_efficiency"
    result = attributes[["model_id", "model_name"]].rename(columns={"model_name": "model"}).merge(
        compatible[[
            "model_id", "ttft_benefit_score", "speed_benefit_score", "latency_benefit_score",
            "engineering_efficiency_score", "q1_performance_score", "deployment_score",
            "efficiency_rank", "deployment_rank", "analysis_status",
        ]], on="model_id", how="left",
    )
    result["analysis_status"] = result["analysis_status"].fillna("excluded_incompatible_or_missing_performance")
    return result


def perturbed_q1_scores(normalized: pd.DataFrame, metrics: list[str], critic: dict[str, float]):
    for metric in metrics:
        for factor in PERTURBATION_FACTORS:
            adjusted = dict(critic)
            adjusted[metric] *= factor
            total = sum(adjusted.values())
            adjusted = {key: value / total for key, value in adjusted.items()}
            yield metric, factor, topsis_scores(normalized, metrics, adjusted)


def q3_sensitivity(
    normalized: pd.DataFrame,
    metrics: list[str],
    critic: dict[str, float],
    costs: dict[str, float],
) -> pd.DataFrame:
    rows = []
    for metric, factor, ranking in perturbed_q1_scores(normalized, metrics, critic):
        performance = ranking.set_index("model_id")["topsis_score"].to_dict()
        ranks = ranking.set_index("model_id")["rank"].astype(int).to_dict()
        frontier = []
        for model in performance:
            dominated = any(
                other != model and costs[other] <= costs[model] and performance[other] >= performance[model]
                and (costs[other] < costs[model] or performance[other] > performance[model])
                for other in performance
            )
            if not dominated:
                frontier.append(model)
        row: dict[str, object] = {
            "perturbed_metric": metric,
            "factor": factor,
            "kimi_score": performance["kimi-k3"],
            "kimi_rank": ranks["kimi-k3"],
            "kimi_on_pareto_frontier": "kimi-k3" in frontier,
            "pareto_frontier_model_ids": ";".join(sorted(frontier)),
        }
        for budget in BUDGETS:
            feasible = [model for model in performance if costs[model] <= budget]
            winner = max(feasible, key=lambda model: (performance[model], -costs[model]))
            row[f"budget_{int(budget)}_recommendation"] = winner
        rows.append(row)
    return pd.DataFrame(rows)


def kimi_cost_analysis(
    performance_cost: pd.DataFrame,
    pareto: pd.DataFrame,
    budgets: pd.DataFrame,
    engineering: pd.DataFrame,
    sensitivity: pd.DataFrame,
) -> pd.DataFrame:
    base = performance_cost.loc[performance_cost["model_id"] == "kimi-k3"].iloc[0]
    pareto_row = pareto.loc[pareto["model_id"] == "kimi-k3"].iloc[0]
    engineering_row = engineering.loc[engineering["model_id"] == "kimi-k3"].iloc[0]
    recommended = budgets.loc[budgets["recommended_model_id"] == "kimi-k3", "budget_limit_usd"].tolist()
    return pd.DataFrame([{
        "model_id": "kimi-k3",
        "model": "Kimi K3",
        "q1_performance_score": base["q1_performance_score"],
        "q1_rank": base["q1_rank"],
        "standard_workload_cost_usd": base["standard_workload_cost_usd"],
        "cost_rank_among_ranked": base["cost_rank_among_ranked"],
        "performance_per_usd": base["performance_per_usd"],
        "value_rank_among_ranked": base["value_rank_among_ranked"],
        "pareto_status": pareto_row["pareto_status"],
        "recommended_budget_levels_usd": ";".join(str(int(value)) for value in recommended),
        "engineering_efficiency_score": engineering_row["engineering_efficiency_score"],
        "efficiency_rank": engineering_row["efficiency_rank"],
        "deployment_score": engineering_row["deployment_score"],
        "deployment_rank": engineering_row["deployment_rank"],
        "main_frontier_competitor": "Claude Fable 5",
        "same_cost_competitor": "GPT-5.5",
        "sensitivity_pareto_probability": float(sensitivity["kimi_on_pareto_frontier"].mean()),
        "sensitivity_budget_recommendation_rate": float(
            sensitivity[[column for column in sensitivity if column.startswith("budget_")]].eq("kimi-k3").to_numpy().mean()
        ),
        "positioning": "高性能、同档最低成本、Pareto前沿；预算达到20美元时由Claude Fable 5取代",
    }])


def final_summary(
    root: Path,
    q2_dir: Path,
    q1: pd.DataFrame,
    performance_cost: pd.DataFrame,
    pareto: pd.DataFrame,
    budgets: pd.DataFrame,
    engineering: pd.DataFrame,
) -> pd.DataFrame:
    q2 = pd.read_csv(q2_dir / "scenario_rankings.csv", encoding="utf-8-sig")
    summary = q1[["model_id", "model", "topsis_score", "rank"]].rename(columns={"topsis_score": "q1_score", "rank": "q1_rank"})
    for scenario, prefix in (("research_long_text", "research"), ("daily_dialogue", "dialogue"), ("code_development", "coding")):
        subset = q2.loc[q2["scenario"] == scenario, ["model_id", "topsis_score", "rank"]].rename(
            columns={"topsis_score": f"{prefix}_score", "rank": f"{prefix}_rank"}
        )
        summary = summary.merge(subset, on="model_id", how="left")
    summary = summary.merge(performance_cost[[
        "model_id", "standard_workload_cost_usd", "cost_rank_among_ranked", "cost_benefit_index",
        "performance_per_usd", "value_rank_among_ranked",
    ]], on="model_id", how="left")
    summary = summary.merge(pareto[["model_id", "pareto_status"]], on="model_id", how="left")
    recommendations = budgets.groupby("recommended_model_id")["budget_limit_usd"].apply(
        lambda values: ";".join(str(int(value)) for value in values)
    ).to_dict()
    summary["recommended_budget_levels_usd"] = summary["model_id"].map(recommendations).fillna("")
    summary = summary.merge(engineering[[
        "model_id", "engineering_efficiency_score", "efficiency_rank", "deployment_score", "deployment_rank",
    ]], on="model_id", how="left")
    return summary


def run_analysis(
    root: Path,
    output_dir: Path,
    q2_dir: Path | None = None,
    summary_path: Path | None = None,
) -> dict[str, object]:
    q2_dir = q2_dir or root / "results/q2"
    summary_path = summary_path or root / "results/final_model_summary.csv"
    attributes = pd.read_csv(root / "data/processed/model_attributes.csv", encoding="utf-8-sig")
    attributes["efficiency_compatible"] = attributes["efficiency_compatible"].astype(str).str.lower().eq("true")
    q1 = pd.read_csv(root / "results/q1/topsis_ranking.csv", encoding="utf-8-sig")
    normalized = pd.read_csv(root / "results/q1/normalized_data.csv", encoding="utf-8-sig").set_index("model_id")
    weight_frame = pd.read_csv(root / "results/q1/critic_weights.csv", encoding="utf-8-sig")
    metrics = weight_frame["metric"].tolist()
    critic = weight_frame.set_index("metric")["weight"].astype(float).to_dict()
    audit = cost_audit(attributes, q1)
    performance_cost = performance_cost_table(audit, q1)
    pareto = pareto_table(performance_cost)
    budgets = budget_selection(performance_cost)
    regression_frame = regression(performance_cost)
    engineering = engineering_efficiency(attributes, q1)
    costs = performance_cost.set_index("model_id")["standard_workload_cost_usd"].astype(float).to_dict()
    sensitivity = q3_sensitivity(normalized, metrics, critic, costs)
    kimi = kimi_cost_analysis(performance_cost, pareto, budgets, engineering, sensitivity)
    summary = final_summary(root, q2_dir, q1, performance_cost, pareto, budgets, engineering)
    outputs = {
        "cost_data_audit.csv": audit,
        "performance_cost.csv": performance_cost,
        "pareto_analysis.csv": pareto,
        "budget_selection.csv": budgets,
        "performance_cost_regression.csv": regression_frame,
        "deploy_scores.csv": engineering,
        "kimi_k3_cost_analysis.csv": kimi,
        "sensitivity_analysis.csv": sensitivity,
    }
    for name, frame in outputs.items():
        write_csv(frame, output_dir / name)
    write_csv(summary, summary_path)
    return {
        "attributes": attributes,
        "q1": q1,
        "normalized": normalized,
        "weights": weight_frame,
        "audit": audit,
        "performance_cost": performance_cost,
        "pareto": pareto,
        "budgets": budgets,
        "regression": regression_frame,
        "engineering": engineering,
        "kimi": kimi,
        "sensitivity": sensitivity,
        "summary": summary,
    }
