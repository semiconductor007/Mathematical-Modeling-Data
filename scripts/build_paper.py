"""Build the Chinese modeling report PDF with Pandoc and XeLaTeX."""

from __future__ import annotations

import shutil
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper" / "modeling_report.md"
OUTPUT = ROOT / "output" / "pdf" / "modeling_report_draft.pdf"


def require_program(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise RuntimeError(f"Required program is not on PATH: {name}")
    return path


def main() -> int:
    pandoc = require_program("pandoc")
    require_program("xelatex")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    command = [
        pandoc, str(SOURCE), "--from=markdown+tex_math_dollars+tex_math_single_backslash",
        "--pdf-engine=xelatex", "--toc", "--toc-depth=2",
        "--resource-path", os.pathsep.join((str(ROOT / "paper"), str(ROOT))),
        "-V", "CJKmainfont=Microsoft YaHei",
        "-V", "mainfont=Times New Roman", "-V", "monofont=Consolas",
        "-V", "geometry:margin=2.2cm", "-V", "fontsize=11pt",
        "-V", "linestretch=1.15", "-V", "colorlinks=true",
        "-V", "linkcolor=blue", "-V", "urlcolor=blue",
        "-o", str(OUTPUT),
    ]
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode:
        return completed.returncode
    print(f"Built {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(2) from exc
