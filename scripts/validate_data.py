"""Validate raw CSV files and report issues without modifying data."""

from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NA_VALUES = {"", "na", "n/a", "null", "none"}
DATA_CUTOFF_DATE = date.fromisoformat("2026-08-17")

FILES = {
    "candidates": ROOT / "data/model_candidates.csv",
    "benchmark": ROOT / "data/raw/benchmark_scores.csv",
    "metadata": ROOT / "data/raw/model_metadata.csv",
    "efficiency": ROOT / "data/raw/cost_efficiency.csv",
}
SOURCE_FILES = {
    "benchmark_sources": ROOT / "data/sources/benchmark_sources.csv",
    "metadata_sources": ROOT / "data/sources/metadata_sources.csv",
    "efficiency_sources": ROOT / "data/sources/efficiency_sources.csv",
}
CORE_SELECTION = ROOT / "results/core_indicator_selection.csv"


def missing(value: str | None) -> bool:
    return value is None or value.strip().lower() in NA_VALUES


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def numeric_or_na(value: str | None) -> bool:
    if value is None or not value.strip():
        return False
    if value.strip() == "NA":
        return True
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def validate_date(value: str | None) -> bool:
    if missing(value):
        return False
    try:
        return date.fromisoformat(value.strip()) <= DATA_CUTOFF_DATE
    except ValueError:
        return False


def date_or_na(value: str | None) -> bool:
    return value == "NA" or validate_date(value)


def main() -> int:
    issues: list[str] = []
    for label, path in (FILES | SOURCE_FILES).items():
        if not path.exists():
            issues.append(f"{label}: missing file {path}")
    if not CORE_SELECTION.exists():
        issues.append(f"core_selection: missing file {CORE_SELECTION}")
    if issues:
        print("\n".join(f"ERROR: {item}" for item in issues))
        return 1

    _, candidates = read_csv(FILES["candidates"])
    _, benchmarks = read_csv(FILES["benchmark"])
    _, metadata = read_csv(FILES["metadata"])
    _, efficiency = read_csv(FILES["efficiency"])
    source_tables = {label: read_csv(path)[1] for label, path in SOURCE_FILES.items()}
    _, core_selection = read_csv(CORE_SELECTION)

    candidate_ids = {r.get("model_id", "").strip() for r in candidates if not missing(r.get("model_id"))}
    if len(candidate_ids) != len([r for r in candidates if not missing(r.get("model_id"))]):
        issues.append("candidates: duplicate model_id")
    allowed_statuses = {"pending", "likely", "excluded", "final"}
    for line, row in enumerate(candidates, start=2):
        if row.get("candidate_status") not in allowed_statuses:
            issues.append(f"candidates:{line}: invalid candidate_status")
        if not validate_date(row.get("release_date")):
            issues.append(f"candidates:{line}: invalid/post-cutoff release_date")
    final_ids = {r["model_id"] for r in candidates if r.get("candidate_status") == "final"}
    if not 6 <= len(final_ids) <= 8:
        issues.append(f"candidates: final model count must be 6-8, got {len(final_ids)}")
    if "kimi-k3" not in final_ids:
        issues.append("candidates: kimi-k3 must be final")

    versions: dict[str, set[str]] = defaultdict(set)
    for label, rows in (("benchmark", benchmarks), ("metadata", metadata), ("efficiency", efficiency)):
        for line, row in enumerate(rows, start=2):
            model_id = row.get("model_id", "").strip()
            if missing(model_id) or model_id not in candidate_ids:
                issues.append(f"{label}:{line}: model_id is missing or absent from candidates: {model_id or 'NA'}")
            model_name = row.get("model_name", "").strip()
            version = row.get("exact_version", "").strip()
            if model_name and version and not missing(version):
                versions[model_name].add(version)

    benchmark_keys = []
    for line, row in enumerate(benchmarks, start=2):
        if not numeric_or_na(row.get("score")):
            issues.append(f"benchmark:{line}: score must be numeric or NA")
        for field in ("source_url", "retrieval_date", "benchmark_version"):
            if missing(row.get(field)):
                issues.append(f"benchmark:{line}: {field} is required")
        if not missing(row.get("retrieval_date")) and not validate_date(row.get("retrieval_date")):
            issues.append(f"benchmark:{line}: invalid/post-cutoff retrieval_date")
        benchmark_keys.append((row.get("model_id"), row.get("benchmark"), row.get("benchmark_version"), row.get("test_setting"), row.get("source_url")))

    price_fields = ("input_price_usd_per_million", "output_price_usd_per_million", "cached_input_price_usd_per_million", "batch_input_price", "batch_output_price", "long_context_price", "peak_price", "off_peak_price")
    metadata_keys = []
    for line, row in enumerate(metadata, start=2):
        for field in price_fields + ("context_window", "max_output_tokens"):
            if not numeric_or_na(row.get(field)):
                issues.append(f"metadata:{line}: {field} must be numeric or NA")
        for field in ("source_url", "retrieval_date", "exact_version"):
            if missing(row.get(field)):
                issues.append(f"metadata:{line}: {field} is required")
        if any(not missing(row.get(field)) for field in price_fields) and missing(row.get("pricing_effective_date")):
            issues.append(f"metadata:{line}: pricing_effective_date required when a price exists")
        for field in ("retrieval_date", "pricing_effective_date"):
            if not date_or_na(row.get(field)):
                issues.append(f"metadata:{line}: invalid/post-cutoff {field}")
        metadata_keys.append((row.get("model_id"), row.get("exact_version"), row.get("source_url")))

    efficiency_keys = []
    for line, row in enumerate(efficiency, start=2):
        for field in ("ttft_seconds", "output_speed_tokens_per_second", "total_latency_seconds"):
            if not numeric_or_na(row.get(field)):
                issues.append(f"efficiency:{line}: {field} must be numeric or NA")
        for field in ("source_url", "retrieval_date"):
            if missing(row.get(field)):
                issues.append(f"efficiency:{line}: {field} is required")
        if row.get("compatible") not in {"true", "false"}:
            issues.append(f"efficiency:{line}: compatible must be true or false")
        if not date_or_na(row.get("measurement_date")):
            issues.append(f"efficiency:{line}: invalid/post-cutoff measurement_date")
        if not validate_date(row.get("retrieval_date")):
            issues.append(f"efficiency:{line}: invalid/post-cutoff retrieval_date")
        efficiency_keys.append((row.get("model_id"), row.get("platform"), row.get("measurement_date"), row.get("test_setting"), row.get("source_url")))

    for label, rows in source_tables.items():
        seen = []
        for line, row in enumerate(rows, start=2):
            if not row.get("source_url", row.get("url", "")).startswith("https://"):
                issues.append(f"{label}:{line}: direct HTTPS source URL is required")
            if not validate_date(row.get("retrieval_date")):
                issues.append(f"{label}:{line}: invalid/post-cutoff retrieval_date")
            if "model_id" in row and row.get("model_id") not in candidate_ids:
                issues.append(f"{label}:{line}: model_id absent from candidates")
            seen.append(tuple(row.values()))
        if len(seen) != len(set(seen)):
            issues.append(f"{label}: exact duplicate source row")

    if not 8 <= len(core_selection) <= 12:
        issues.append(f"core_selection: expected 8-12 indicators, got {len(core_selection)}")
    for line, row in enumerate(core_selection, start=2):
        try:
            best = int(row.get("best_comparable_models", ""))
            total = int(row.get("final_models", ""))
            coverage = float(row.get("coverage", "").rstrip("%"))
        except ValueError:
            issues.append(f"core_selection:{line}: invalid coverage fields")
            continue
        if total != len(final_ids) or best > total:
            issues.append(f"core_selection:{line}: counts do not match final pool")
        if abs(coverage - best / total * 100) > 0.11 or coverage < 75:
            issues.append(f"core_selection:{line}: coverage must be accurate and >=75%")
        if row.get("status") != "core":
            issues.append(f"core_selection:{line}: status must be core")

    for label, keys in (("benchmark", benchmark_keys), ("metadata", metadata_keys), ("efficiency", efficiency_keys)):
        for key, count in Counter(keys).items():
            if count > 1:
                issues.append(f"{label}: duplicate record key ({count} rows): {key}")
    for model_name, model_versions in versions.items():
        if len(model_versions) > 1:
            issues.append(f"version mix: {model_name} has versions {sorted(model_versions)}")

    row_count = len(candidates) + len(benchmarks) + len(metadata) + len(efficiency) + sum(map(len, source_tables.values())) + len(core_selection)
    if issues:
        print(f"Validation completed: {len(issues)} issue(s) across {row_count} row(s).")
        print("\n".join(f"- {item}" for item in issues))
        return 1
    print(f"Validation passed: {row_count} data row(s), no issues found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
