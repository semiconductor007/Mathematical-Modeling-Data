"""Collect auditable Artificial Analysis efficiency candidates into staging.

This script reads only public, explicitly allow-listed model provider pages. It
does not call candidate LLMs, run benchmarks, infer missing values, or write any
raw project table. Output is review-only staging and must not be used for
modeling until manually reviewed and promoted in a later phase.

Examples:
    python scripts/fetch_artificial_analysis_efficiency.py --dry-run
    python scripts/fetch_artificial_analysis_efficiency.py --model-id kimi-k3
    python scripts/fetch_artificial_analysis_efficiency.py --snapshot-dir PATH
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import random
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = Path(__file__).with_name("artificial_analysis_targets.json")
DEFAULT_OUTPUT = ROOT / "results/efficiency_staging.csv"
DEFAULT_CANDIDATE_REF = "HEAD"
USER_AGENT = "TJMML-Member-C-Efficiency-Collector/1.0 (academic research)"
SOURCE_NAME = "Artificial Analysis API Provider Performance Benchmarking"
SOURCE_TYPE = "independent_evaluation"
MISSING = "NA"
REVIEW_MARKER = "NOT FOR MODELING; REVIEW ONLY; NOT RAW DATA"

FIELDS = [
    "model_id",
    "candidate_exact_version",
    "aa_display_name",
    "configuration",
    "reasoning_effort",
    "provider",
    "provider_scope",
    "workload",
    "metric",
    "raw_display_value",
    "raw_unit",
    "normalized_value_candidate",
    "normalized_unit_candidate",
    "source_url",
    "source_name",
    "source_type",
    "measurement_window",
    "retrieval_date",
    "retrieval_timestamp",
    "http_status",
    "content_hash",
    "exact_version_match",
    "configuration_identified",
    "provider_identified",
    "metric_label_verified",
    "candidate_compatible",
    "manual_review_required",
    "review_reason",
    "notes",
]

METRICS = {
    "Time to First Token": ("ttft_seconds", "seconds"),
    "Output Speed": ("output_speed_tokens_per_second", "tokens/s"),
    "End-to-End Response Time": ("end_to_end_500_tokens_seconds", "seconds"),
}


class CollectionError(RuntimeError):
    """Raised when public page content cannot be verified safely."""


class FetchError(CollectionError):
    """Raised when a public HTTP request fails, preserving a known status."""

    def __init__(self, message: str, status: str = MISSING) -> None:
        super().__init__(message)
        self.status = status


@dataclass(frozen=True)
class FetchResult:
    url: str
    status: int
    body: bytes
    timestamp: str

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.body).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--candidate-ref", default=DEFAULT_CANDIDATE_REF)
    parser.add_argument("--model-id", action="append", dest="model_ids")
    parser.add_argument("--delay", type=float, default=2.5)
    parser.add_argument("--jitter", type=float, default=0.5)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--retrieval-date", default=date.today().isoformat())
    parser.add_argument("--snapshot-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Revisit same-date targets; identical content is still deduplicated.",
    )
    args = parser.parse_args()
    if args.delay < 2:
        parser.error("--delay must be at least 2 seconds")
    if args.jitter < 0:
        parser.error("--jitter must be non-negative")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if not 0 <= args.retries <= 5:
        parser.error("--retries must be between 0 and 5")
    try:
        date.fromisoformat(args.retrieval_date)
    except ValueError:
        parser.error("--retrieval-date must be YYYY-MM-DD")
    return args


def read_candidate_versions(ref: str) -> dict[str, str]:
    command = ["git", "show", f"{ref}:data/model_candidates.csv"]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise CollectionError(
            f"Cannot read candidate table from {ref}: {completed.stderr.strip()}"
        )
    rows = csv.DictReader(completed.stdout.splitlines())
    candidates = {
        row["model_id"].strip(): row["exact_version"].strip()
        for row in rows
        if row.get("model_id", "").strip()
    }
    if not candidates:
        raise CollectionError(f"Candidate table at {ref} is empty")
    return candidates


def load_targets(path: Path, candidates: dict[str, str]) -> list[dict[str, Any]]:
    try:
        targets = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CollectionError(f"Cannot load target configuration {path}: {exc}") from exc
    if not isinstance(targets, list):
        raise CollectionError("Target configuration must be a JSON array")

    required = {
        "model_id",
        "candidate_exact_version",
        "aa_slug",
        "aa_display_name",
        "configuration",
        "reasoning_effort",
        "provider",
        "provider_scope",
        "url",
        "status",
        "candidate_compatible",
        "review_reason",
    }
    seen: set[tuple[str, str, str]] = set()
    for index, target in enumerate(targets, start=1):
        if not isinstance(target, dict):
            raise CollectionError(f"Target {index} is not an object")
        missing_keys = sorted(required - target.keys())
        if missing_keys:
            raise CollectionError(f"Target {index} lacks keys: {missing_keys}")
        model_id = str(target["model_id"])
        if model_id not in candidates:
            raise CollectionError(f"Target model_id is absent from {DEFAULT_CANDIDATE_REF}: {model_id}")
        if str(target["candidate_exact_version"]) != candidates[model_id]:
            raise CollectionError(
                f"Exact-version mismatch for {model_id}: config={target['candidate_exact_version']!r}, "
                f"candidate={candidates[model_id]!r}"
            )
        parsed = urlparse(str(target["url"]))
        if parsed.scheme != "https" or parsed.netloc != "artificialanalysis.ai":
            raise CollectionError(f"Target URL is not an approved AA HTTPS page: {target['url']}")
        if not parsed.path.startswith("/models/") or not parsed.path.endswith("/providers"):
            raise CollectionError(f"Target must be an explicit model providers page: {target['url']}")
        if target["provider_scope"] not in {
            "model_aggregate",
            "first_party",
            "specific_provider",
            "unknown",
        }:
            raise CollectionError(f"Invalid provider_scope for {model_id}")
        key = (model_id, str(target["configuration"]), str(target["provider"]))
        if key in seen:
            raise CollectionError(f"Duplicate target configuration: {key}")
        seen.add(key)
    return targets


def fetch_public_html(url: str, timeout: float, retries: int) -> FetchResult:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        },
        method="GET",
    )
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                final_url = response.geturl()
                if urlparse(final_url).netloc != "artificialanalysis.ai":
                    raise CollectionError(f"Unexpected redirect outside AA: {final_url}")
                status = int(response.status)
                body = response.read()
                if status != 200:
                    raise FetchError(f"Unexpected HTTP status {status}", str(status))
                content_type = response.headers.get_content_type()
                if content_type not in {"text/html", "application/xhtml+xml"}:
                    raise FetchError(f"Unexpected content type: {content_type}", str(status))
                if not body:
                    raise FetchError("Empty response body", str(status))
                if len(body) > 10 * 1024 * 1024:
                    raise FetchError("Response exceeds 10 MiB safety limit", str(status))
                timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
                return FetchResult(final_url, status, body, timestamp)
        except HTTPError as exc:
            last_error = FetchError(f"HTTP error {exc.code}", str(exc.code))
            if attempt < retries:
                time.sleep(min(2 ** attempt, 4))
        except (URLError, TimeoutError, OSError, CollectionError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(2 ** attempt, 4))
    status = last_error.status if isinstance(last_error, FetchError) else MISSING
    raise FetchError(
        f"Fetch failed after {retries + 1} attempt(s): {last_error}", status
    )


def decode_public_html(body: bytes) -> str:
    try:
        decoded = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CollectionError("Response is not valid UTF-8 HTML") from exc
    # Next.js returns public server-rendered data inside escaped script text.
    decoded = html.unescape(decoded).replace('\\"', '"')
    return decoded


def extract_balanced_object(text: str, start: int) -> str:
    if not text.startswith("{", start):
        raise CollectionError("JSON object start not found")
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise CollectionError("Unbalanced JSON object in page")


def provider_objects(page: str, aa_slug: str) -> list[dict[str, Any]]:
    marker = f'"model":{{"slug":"{aa_slug}"}}'
    results: dict[str, dict[str, Any]] = {}
    search_from = 0
    while True:
        position = page.find(marker, search_from)
        if position < 0:
            break
        start = page.rfind('{"id":', max(0, position - 6000), position)
        if start >= 0:
            try:
                item = json.loads(extract_balanced_object(page, start))
            except (json.JSONDecodeError, CollectionError):
                item = None
            if isinstance(item, dict):
                model = item.get("model") or {}
                host = item.get("host") or {}
                performance = item.get("performance") or {}
                if model.get("slug") == aa_slug and host.get("label") and performance:
                    results[str(item.get("slug", host.get("label")))] = item
        search_from = position + len(marker)
    return list(results.values())


def number_string(value: Any) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return MISSING
    return format(value, ".15g")


def find_metric_values(item: dict[str, Any]) -> dict[str, str]:
    performance = item.get("performance")
    if not isinstance(performance, dict):
        return {name: MISSING for name in METRICS}
    output_speed = performance.get("outputSpeed") or {}
    ttft = performance.get("timeToFirstToken") or {}
    end_to_end = performance.get("endToEndResponseTime") or {}
    return {
        "Time to First Token": number_string(ttft.get("median")),
        "Output Speed": number_string(output_speed.get("median")),
        "End-to-End Response Time": number_string(end_to_end.get("totalTime")),
    }


def metric_labels(page: str) -> dict[str, bool]:
    return {
        "Time to First Token": "Time to First Token" in page,
        "Output Speed": "Output Speed" in page,
        "End-to-End Response Time": "End-to-End Response Time" in page
        and "Seconds to output 500 tokens" in page,
    }


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def na_safe(value: Any) -> str:
    text_value = str(value).strip() if value is not None else ""
    return text_value or MISSING


def failure_rows(
    target: dict[str, Any], retrieval_date: str, reason: str, status: str = MISSING
) -> list[dict[str, str]]:
    rows = []
    for metric_name, (_, unit) in METRICS.items():
        rows.append(
            make_row(
                target=target,
                retrieval_date=retrieval_date,
                retrieval_timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                http_status=status,
                content_hash=MISSING,
                metric_name=metric_name,
                value=MISSING,
                unit=unit,
                exact_match=False,
                provider_found=False,
                label_verified=False,
                review_reason=reason,
            )
        )
    return rows


def make_row(
    *,
    target: dict[str, Any],
    retrieval_date: str,
    retrieval_timestamp: str,
    http_status: str,
    content_hash: str,
    metric_name: str,
    value: str,
    unit: str,
    exact_match: bool,
    provider_found: bool,
    label_verified: bool,
    review_reason: str,
) -> dict[str, str]:
    has_value = value != MISSING
    manual_review = (
        target.get("status") != "confirmed"
        or not exact_match
        or not provider_found
        or not label_verified
        or not has_value
        or not bool(target.get("candidate_compatible"))
    )
    _, normalized_unit = METRICS[metric_name]
    row = {
        "model_id": target["model_id"],
        "candidate_exact_version": target["candidate_exact_version"],
        "aa_display_name": target["aa_display_name"],
        "configuration": target["configuration"],
        "reasoning_effort": target["reasoning_effort"],
        "provider": target["provider"],
        "provider_scope": target["provider_scope"],
        "workload": "10k input tokens; single prompt; 500-token standardized E2E",
        "metric": metric_name,
        "raw_display_value": value,
        "raw_unit": unit,
        "normalized_value_candidate": value,
        "normalized_unit_candidate": normalized_unit,
        "source_url": target["url"],
        "source_name": SOURCE_NAME,
        "source_type": SOURCE_TYPE,
        "measurement_window": "median (P50) over past 72 hours",
        "retrieval_date": retrieval_date,
        "retrieval_timestamp": retrieval_timestamp,
        "http_status": http_status,
        "content_hash": content_hash,
        "exact_version_match": bool_text(exact_match),
        "configuration_identified": bool_text(target["configuration"] != MISSING),
        "provider_identified": bool_text(provider_found),
        "metric_label_verified": bool_text(label_verified),
        "candidate_compatible": bool_text(bool(target.get("candidate_compatible"))),
        "manual_review_required": bool_text(manual_review),
        "review_reason": review_reason,
        "notes": (
            f"{REVIEW_MARKER}; value read from AA public server-rendered performance data; "
            "E2E is AA's directly published standardized 500-token totalTime, not an arbitrary-length answer."
        ),
    }
    return {field: na_safe(row.get(field)) for field in FIELDS}


def existing_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if rows and set(rows[0]) != set(FIELDS):
        raise CollectionError(f"Existing staging schema does not match collector schema: {path}")
    return rows


def identity_key(row: dict[str, str]) -> tuple[str, ...]:
    return (
        row["model_id"],
        row["configuration"],
        row["provider"],
        row["metric"],
        row["source_url"],
        row["retrieval_date"],
    )


def exact_evidence_key(row: dict[str, str]) -> tuple[str, ...]:
    return identity_key(row) + (row["content_hash"], row["raw_display_value"])


def write_rows(path: Path, old_rows: list[dict[str, str]], new_rows: Iterable[dict[str, str]]) -> int:
    evidence = {exact_evidence_key(row) for row in old_rows}
    additions = []
    for row in new_rows:
        key = exact_evidence_key(row)
        if key not in evidence:
            additions.append(row)
            evidence.add(key)
    if not additions:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows([*old_rows, *additions])
    return len(additions)


def save_snapshot(directory: Path, target: dict[str, Any], fetched: FetchResult) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    stamp = fetched.timestamp.replace(":", "").replace("+00:00", "Z")
    provider = "".join(c if c.isalnum() else "-" for c in target["provider"]).strip("-")
    filename = f"{target['model_id']}__{provider}__{stamp}__{fetched.sha256[:12]}.html"
    path = directory / filename
    if not path.exists():
        path.write_bytes(fetched.body)
    return path


def collect_target(
    target: dict[str, Any], args: argparse.Namespace, candidate_versions: dict[str, str]
) -> list[dict[str, str]]:
    exact_match = candidate_versions.get(target["model_id"]) == target["candidate_exact_version"]
    try:
        fetched = fetch_public_html(target["url"], args.timeout, args.retries)
        page = decode_public_html(fetched.body)
        if target["aa_display_name"] not in page:
            raise CollectionError(
                f"AA display name not found in page: {target['aa_display_name']}"
            )
        items = provider_objects(page, target["aa_slug"])
        selected = [item for item in items if (item.get("host") or {}).get("label") == target["provider"]]
        if len(selected) != 1:
            raise CollectionError(
                f"Expected one provider object for {target['provider']!r}; found {len(selected)}"
            )
        provider_item = selected[0]
        values = find_metric_values(provider_item)
        labels = metric_labels(page)
        if args.snapshot_dir:
            save_snapshot(args.snapshot_dir, target, fetched)
        rows = []
        for metric_name, (_, unit) in METRICS.items():
            reason_parts = [target["review_reason"]]
            if values[metric_name] == MISSING:
                reason_parts.append("Direct metric value is absent from the provider performance object.")
            if not labels[metric_name]:
                reason_parts.append("Expected metric label is absent from the public page.")
            rows.append(
                make_row(
                    target=target,
                    retrieval_date=args.retrieval_date,
                    retrieval_timestamp=fetched.timestamp,
                    http_status=str(fetched.status),
                    content_hash=fetched.sha256,
                    metric_name=metric_name,
                    value=values[metric_name],
                    unit=unit,
                    exact_match=exact_match,
                    provider_found=True,
                    label_verified=labels[metric_name],
                    review_reason=" ".join(reason_parts),
                )
            )
        return rows
    except FetchError as exc:
        return failure_rows(target, args.retrieval_date, str(exc), exc.status)
    except CollectionError as exc:
        return failure_rows(target, args.retrieval_date, str(exc))


def main() -> int:
    args = parse_args()
    try:
        candidates = read_candidate_versions(args.candidate_ref)
        targets = load_targets(args.config, candidates)
        if args.model_ids:
            requested = set(args.model_ids)
            unknown = requested - {target["model_id"] for target in targets}
            if unknown:
                raise CollectionError(f"Unknown --model-id values: {sorted(unknown)}")
            targets = [target for target in targets if target["model_id"] in requested]
        current_rows = existing_rows(args.output)
    except CollectionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Candidate source: {args.candidate_ref} ({len(candidates)} models)")
    print(f"Allow-list: {args.config} ({len(targets)} selected targets)")
    print(f"Output: {args.output} [{REVIEW_MARKER}]")
    for target in targets:
        print(
            f"- {target['model_id']} | {target['configuration']} | "
            f"{target['provider']} | {target['url']}"
        )
    if args.dry_run:
        print("Dry-run complete: no HTTP requests sent and no staging file written.")
        return 0

    same_date_keys = {identity_key(row) for row in current_rows}
    all_new_rows: list[dict[str, str]] = []
    visited = 0
    for index, target in enumerate(targets):
        expected_keys = {
            (
                target["model_id"],
                target["configuration"],
                target["provider"],
                metric,
                target["url"],
                args.retrieval_date,
            )
            for metric in METRICS
        }
        if not args.refresh and expected_keys.issubset(same_date_keys):
            print(f"SKIP {target['model_id']}: same-date staging records already exist")
            continue
        if visited and index:
            wait_seconds = args.delay + random.uniform(0, args.jitter)
            time.sleep(wait_seconds)
        print(f"FETCH {target['model_id']}: {target['url']}")
        rows = collect_target(target, args, candidates)
        all_new_rows.extend(rows)
        visited += 1

    try:
        added = write_rows(args.output, current_rows, all_new_rows)
    except (OSError, CollectionError) as exc:
        print(f"ERROR: cannot write staging output: {exc}", file=sys.stderr)
        return 3
    values = [row for row in all_new_rows if row["raw_display_value"] != MISSING]
    print(
        f"Collection complete: visited={visited}, candidate rows={len(all_new_rows)}, "
        f"numeric rows={len(values)}, appended={added}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
