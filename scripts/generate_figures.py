"""Generate dependency-free SVG figures from committed result tables."""

from __future__ import annotations

import argparse
import csv
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "figures"
COLORS = ["#2563eb", "#0f766e", "#7c3aed", "#ea580c", "#475569", "#dc2626"]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def save(path: Path, body: str, width: int, height: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        '<rect width="100%" height="100%" fill="white"/>'
        '<style>text{font-family:Arial,"Microsoft YaHei",sans-serif;fill:#172033}.title{font-size:22px;font-weight:700}.label{font-size:14px}.small{font-size:12px;fill:#475569}</style>'
        + body + "</svg>"
    )
    path.write_text(svg, encoding="utf-8")


def bar_chart(path: Path, title: str, labels: list[str], values: list[float], value_format: str = ".3f") -> None:
    width, left, right, top, row_height = 900, 210, 70, 70, 46
    height = top + len(labels) * row_height + 45
    maximum = max(values) if values else 1
    plot_width = width - left - right
    parts = [f'<text class="title" x="{width/2}" y="34" text-anchor="middle">{escape(title)}</text>']
    for index, (label, value) in enumerate(zip(labels, values)):
        y = top + index * row_height
        bar_width = plot_width * value / maximum if maximum else 0
        parts.append(f'<text class="label" x="{left-12}" y="{y+20}" text-anchor="end">{escape(label)}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" height="27" rx="4" fill="{COLORS[index % len(COLORS)]}"/>')
        parts.append(f'<text class="label" x="{left+bar_width+8:.1f}" y="{y+20}">{format(value, value_format)}</text>')
    save(path, "".join(parts), width, height)


def generate(output_dir: Path) -> list[Path]:
    ranking = [row for row in read_rows(ROOT / "results/phase4/general_ranking.csv") if row["topsis_score"] != "NA"]
    ranking.sort(key=lambda row: int(row["rank"]))
    bar_chart(
        output_dir / "general_ranking.svg", "CRITIC–TOPSIS 综合排名",
        [row["model_name"] for row in ranking], [float(row["topsis_score"]) for row in ranking],
    )
    weights = read_rows(ROOT / "results/phase4/critic_weights.csv")
    weights.sort(key=lambda row: float(row["critic_weight"]), reverse=True)
    bar_chart(
        output_dir / "critic_weights.svg", "CRITIC 指标权重",
        [row["indicator"] for row in weights], [float(row["critic_weight"]) for row in weights],
    )

    scenario = [row for row in read_rows(ROOT / "results/phase5/scenario_rankings.csv") if row["scenario_rank"] != "NA"]
    scenarios = list(dict.fromkeys(row["scenario"] for row in scenario))
    models = list(dict.fromkeys(row["model_name"] for row in scenario))
    width, height = 950, 410
    x_positions = [190, 470, 750]
    parts = [f'<text class="title" x="{width/2}" y="34" text-anchor="middle">三类场景排名变化（1 为最佳）</text>']
    for x, name in zip(x_positions, scenarios):
        parts.append(f'<text class="label" x="{x}" y="68" text-anchor="middle">{escape(name)}</text>')
        parts.append(f'<line x1="{x}" y1="90" x2="{x}" y2="330" stroke="#cbd5e1"/>')
        for rank in range(1, 6):
            y = 90 + (rank - 1) * 60
            parts.append(f'<text class="small" x="{x-18}" y="{y+4}" text-anchor="end">{rank}</text>')
    for index, model in enumerate(models):
        points = []
        for x, name in zip(x_positions, scenarios):
            row = next(item for item in scenario if item["scenario"] == name and item["model_name"] == model)
            y = 90 + (int(row["scenario_rank"]) - 1) * 60
            points.append((x, y))
        color = COLORS[index]
        parts.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="3"/>')
        for x, y in points:
            parts.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{color}"/>')
        parts.append(f'<text class="small" x="{x_positions[-1]+18}" y="{points[-1][1]+4}" fill="{color}">{escape(model)}</text>')
    save(output_dir / "scenario_rank_changes.svg", "".join(parts), width, height)

    cost = [row for row in read_rows(ROOT / "results/phase6/performance_cost.csv") if row["analysis_status"] == "included"]
    width, height, left, bottom, top, right = 900, 520, 90, 70, 60, 100
    max_cost = max(float(row["standardized_api_cost_usd"]) for row in cost) * 1.1
    max_score = max(float(row["general_performance_score"]) for row in cost) * 1.1
    parts = [f'<text class="title" x="{width/2}" y="34" text-anchor="middle">性能—API 成本 Pareto 前沿</text>']
    parts += [
        f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#334155"/>',
        f'<line x1="{left}" y1="{height-bottom}" x2="{left}" y2="{top}" stroke="#334155"/>',
        f'<text class="label" x="{(left+width-right)/2}" y="{height-20}" text-anchor="middle">标准工作负载 API 成本（USD）</text>',
        f'<text class="label" transform="translate(24 {(top+height-bottom)/2}) rotate(-90)" text-anchor="middle">综合性能得分</text>',
    ]
    frontier_points = []
    for index, row in enumerate(cost):
        x = left + float(row["standardized_api_cost_usd"]) / max_cost * (width - left - right)
        y = height - bottom - float(row["general_performance_score"]) / max_score * (height - top - bottom)
        color = "#dc2626" if row["pareto_frontier"] == "true" else "#64748b"
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{color}"/>')
        parts.append(f'<text class="small" x="{x+10:.1f}" y="{y-9:.1f}">{escape(row["model_name"])}</text>')
        if row["pareto_frontier"] == "true":
            frontier_points.append((x, y))
    frontier_points.sort()
    if len(frontier_points) > 1:
        parts.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in frontier_points)}" fill="none" stroke="#dc2626" stroke-width="2" stroke-dasharray="6 4"/>')
    save(output_dir / "performance_cost_pareto.svg", "".join(parts), width, height)
    return [
        output_dir / "general_ranking.svg", output_dir / "critic_weights.svg",
        output_dir / "scenario_rank_changes.svg", output_dir / "performance_cost_pareto.svg",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    paths = generate(args.output_dir)
    print(f"Generated {len(paths)} SVG figures in {args.output_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
