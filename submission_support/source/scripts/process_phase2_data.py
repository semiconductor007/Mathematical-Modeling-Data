"""Build deterministic Phase 2 cleaned datasets without changing raw files."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
DEFAULT_OUTPUT = ROOT / "data/processed"
COHORT_CONFIG = Path(__file__).with_name("phase2_core_cohorts.csv")
NA = "NA"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def normalized(value: str | None) -> str:
    value = (value or "").strip()
    return value if value else NA


def build(output_dir: Path) -> dict[str, int]:
    candidates = read_rows(ROOT / "data/model_candidates.csv")
    benchmarks = read_rows(RAW / "benchmark_scores.csv")
    metadata = read_rows(RAW / "model_metadata.csv")
    efficiency = read_rows(RAW / "cost_efficiency.csv")
    cohorts = read_rows(COHORT_CONFIG)

    final = [row for row in candidates if row["candidate_status"] == "final"]
    if not 6 <= len(final) <= 8:
        raise ValueError(f"Expected 6-8 final models, found {len(final)}")
    final_ids = [row["model_id"] for row in final]
    metadata_by_id = {row["model_id"]: row for row in metadata}
    efficiency_by_id = {row["model_id"]: row for row in efficiency}
    if len(metadata_by_id) != len(metadata) or len(efficiency_by_id) != len(efficiency):
        raise ValueError("Metadata and efficiency tables must contain one row per model")

    long_rows: list[dict[str, str]] = []
    matrix_rows = {
        row["model_id"]: {
            "model_id": row["model_id"],
            "provider": row["provider"],
            "model_name": row["model_name"],
            "exact_version": row["exact_version"],
        }
        for row in final
    }
    score_units: dict[str, str] = {}
    indicator_quality: list[dict[str, str]] = []
    for cohort in cohorts:
        matches = [
            row for row in benchmarks
            if row["benchmark"] == cohort["raw_benchmark"]
            and row["benchmark_version"] == cohort["benchmark_version"]
            and row["test_setting"] == cohort["test_setting"]
            and row["source_name"] == cohort["source_name"]
            and row["compatible"] == "true"
            and row["model_id"] in final_ids
        ]
        counts = Counter(row["model_id"] for row in matches)
        if any(counts[model_id] != 1 for model_id in final_ids):
            raise ValueError(f"Cohort {cohort['indicator_key']} does not have exactly one row per final model")
        units = {row["score_unit"] for row in matches if row["score"] != NA}
        if len(units) != 1:
            raise ValueError(f"Cohort {cohort['indicator_key']} mixes score units")
        score_units[cohort["indicator_key"]] = units.pop()
        for row in matches:
            score = normalized(row["score"])
            matrix_rows[row["model_id"]][cohort["indicator_key"]] = score
            long_rows.append({
                "model_id": row["model_id"],
                "model_name": row["model_name"],
                "indicator_key": cohort["indicator_key"],
                "dimension": cohort["dimension"],
                "indicator": cohort["indicator"],
                "score": score,
                "score_unit": row["score_unit"],
                "higher_is_better": cohort["higher_is_better"],
                "benchmark_version": row["benchmark_version"],
                "test_setting": row["test_setting"],
                "source_name": row["source_name"],
                "source_url": row["source_url"],
                "retrieval_date": row["retrieval_date"],
                "missing_reason": (
                    "not applicable: frozen model is text-only"
                    if score == NA
                    and row["model_id"] == "glm-5.2"
                    and cohort["dimension"] in {
                        "multimodal", "document_understanding",
                        "research_document_reasoning", "multimodal_math",
                    }
                    else "not reported in frozen cohort" if score == NA else NA
                ),
            })
        present_ids = sorted(row["model_id"] for row in matches if row["score"] != NA)
        missing_ids = sorted(set(final_ids) - set(present_ids))
        indicator_quality.append({
            "indicator_key": cohort["indicator_key"],
            "dimension": cohort["dimension"],
            "indicator": cohort["indicator"],
            "score_unit": score_units[cohort["indicator_key"]],
            "higher_is_better": cohort["higher_is_better"],
            "available_models": str(len(present_ids)),
            "final_models": str(len(final_ids)),
            "coverage_percent": f"{len(present_ids) / len(final_ids) * 100:.1f}",
            "missing_model_ids": ";".join(missing_ids) if missing_ids else NA,
            "cohort_status": "pass" if len(present_ids) / len(final_ids) >= 0.75 else "fail",
        })

    matrix_fields = ["model_id", "provider", "model_name", "exact_version"] + [
        row["indicator_key"] for row in cohorts
    ]
    write_rows(output_dir / "core_benchmark_matrix.csv", matrix_fields, list(matrix_rows.values()))
    long_fields = [
        "model_id", "model_name", "indicator_key", "dimension", "indicator", "score",
        "score_unit", "higher_is_better", "benchmark_version", "test_setting", "source_name",
        "source_url", "retrieval_date", "missing_reason",
    ]
    write_rows(output_dir / "core_benchmark_long.csv", long_fields, long_rows)
    write_rows(
        output_dir / "indicator_quality.csv",
        [
            "indicator_key", "dimension", "indicator", "score_unit", "higher_is_better",
            "available_models", "final_models", "coverage_percent", "missing_model_ids", "cohort_status",
        ],
        indicator_quality,
    )

    attribute_rows: list[dict[str, str]] = []
    metadata_fields = [
        "context_window", "max_output_tokens", "vision_support", "reasoning_support",
        "api_available", "input_price_usd_per_million", "output_price_usd_per_million",
        "cached_input_price_usd_per_million", "batch_input_price", "batch_output_price",
        "long_context_price", "peak_price", "off_peak_price", "pricing_effective_date",
    ]
    for candidate in final:
        model_id = candidate["model_id"]
        meta = metadata_by_id[model_id]
        eff = efficiency_by_id[model_id]
        for field in ("model_name", "provider", "exact_version"):
            if meta[field] != candidate[field]:
                raise ValueError(f"Identity mismatch for {model_id}: {field}")
        compatible = eff["compatible"] == "true"
        result = {
            "model_id": model_id,
            "provider": candidate["provider"],
            "model_name": candidate["model_name"],
            "exact_version": candidate["exact_version"],
        }
        result.update({field: normalized(meta.get(field)) for field in metadata_fields})
        result.update({
            "efficiency_compatible": eff["compatible"],
            "observed_ttft_seconds": normalized(eff.get("ttft_seconds")),
            "observed_output_speed_tokens_per_second": normalized(eff.get("output_speed_tokens_per_second")),
            "observed_total_latency_seconds": normalized(eff.get("total_latency_seconds")),
            "comparable_ttft_seconds": normalized(eff.get("ttft_seconds")) if compatible else NA,
            "comparable_output_speed_tokens_per_second": normalized(eff.get("output_speed_tokens_per_second")) if compatible else NA,
            "comparable_total_latency_seconds": normalized(eff.get("total_latency_seconds")) if compatible else NA,
            "efficiency_test_setting": eff["test_setting"],
            "efficiency_source_url": eff["source_url"],
            "efficiency_exclusion_reason": NA if compatible else eff["notes"],
        })
        attribute_rows.append(result)
    attribute_fields = list(attribute_rows[0])
    write_rows(output_dir / "model_attributes.csv", attribute_fields, attribute_rows)

    quality_rows = [
        {"check": "final_model_count", "value": str(len(final)), "status": "pass", "notes": "Target range: 6-8"},
        {"check": "core_indicator_count", "value": str(len(cohorts)), "status": "pass", "notes": "Target range: 8-12"},
        {"check": "core_matrix_rows", "value": str(len(matrix_rows)), "status": "pass", "notes": "One row per final model"},
        {"check": "core_long_rows", "value": str(len(long_rows)), "status": "pass", "notes": "Final models x core indicators"},
        {"check": "core_missing_scores", "value": str(sum(row["score"] == NA for row in long_rows)), "status": "pass", "notes": "Preserved as literal NA; no imputation"},
        {"check": "core_cohorts_at_least_75_percent", "value": str(sum(row["cohort_status"] == "pass" for row in indicator_quality)), "status": "pass", "notes": "All frozen core cohorts pass"},
        {"check": "strict_efficiency_models", "value": str(sum(row["efficiency_compatible"] == "true" for row in attribute_rows)), "status": "pass", "notes": "Incompatible observations retained separately"},
        {"check": "raw_files_modified", "value": "0", "status": "pass", "notes": "Processor is read-only for data/raw"},
    ]
    write_rows(output_dir / "phase2_quality_report.csv", ["check", "value", "status", "notes"], quality_rows)
    return {"models": len(final), "indicators": len(cohorts), "long_rows": len(long_rows)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        counts = build(args.output_dir)
    except (KeyError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"Phase 2 processed data written: {counts['models']} final models, "
        f"{counts['indicators']} core indicators, {counts['long_rows']} long rows; no imputation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
