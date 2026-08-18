"""Generate the modeling-paper overview flowchart."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "paper" / "modeling_flowchart.png"


def main() -> None:
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(12, 5.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")

    nodes = [
        (0.5, 4.2, 2.0, 1.0, "公开数据采集\n版本与口径冻结", "#DCE9F7"),
        (3.1, 4.2, 2.0, 1.0, "覆盖率、方差与\n相关性筛选", "#DCE9F7"),
        (5.7, 4.2, 2.0, 1.0, "CRITIC 客观赋权\nTOPSIS 综合评价", "#D9EAD3"),
        (8.3, 4.2, 2.0, 1.0, "Kimi 优劣势\nGLM 局部定位", "#FCE5CD"),
        (3.1, 1.4, 2.0, 1.0, "三类场景偏好\n组合赋权与排序", "#FFF2CC"),
        (5.7, 1.4, 2.0, 1.0, "标准 API 负载\nPareto 与预算选型", "#FFF2CC"),
        (8.3, 1.4, 2.0, 1.0, "熵权替代与\n36 组扰动检验", "#EADCF8"),
    ]
    for x, y, w, h, label, color in nodes:
        box = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.08",
            facecolor=color, edgecolor="#365F91", linewidth=1.4,
        )
        ax.add_patch(box)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=12)

    arrows = [
        ((2.5, 4.7), (3.1, 4.7)), ((5.1, 4.7), (5.7, 4.7)),
        ((7.7, 4.7), (8.3, 4.7)), ((6.7, 4.2), (4.1, 2.4)),
        ((6.7, 4.2), (6.7, 2.4)), ((5.1, 1.9), (5.7, 1.9)),
        ((7.7, 1.9), (8.3, 1.9)), ((9.3, 4.2), (9.3, 2.4)),
    ]
    for start, end in arrows:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=14,
                                     linewidth=1.3, color="#365F91"))

    ax.text(6, 5.65, "主流大语言模型综合性能评价技术路线", ha="center",
            va="center", fontsize=17, fontweight="bold")
    ax.text(6, 0.55, "数据约束贯穿全流程：不自行测评、不跨口径替换、不插补缺失成绩",
            ha="center", va="center", fontsize=11, color="#7F0000")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Generated {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
