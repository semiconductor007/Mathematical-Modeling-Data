"""Rebuild the competition-paper DOCX from Markdown and committed figures."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper" / "competition_paper.md"
RAW = ROOT / "tmp" / "paper_docx" / "competition_paper_raw.docx"
OUTPUT = ROOT / "output" / "docx" / "competition_paper_draft.docx"


def run(command: list[str]) -> None:
    print("==>", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        print("pandoc is required to build the competition paper", file=sys.stderr)
        return 2
    RAW.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    run([sys.executable, "scripts/generate_paper_flowchart.py"])
    run([
        pandoc, str(SOURCE),
        "--from=markdown+tex_math_dollars+tex_math_single_backslash",
        f"--resource-path={ROOT / 'paper'}{';'}{ROOT}",
        "--reference-location=block", "-o", str(RAW),
    ])
    run([sys.executable, "scripts/format_competition_docx.py", str(RAW), str(OUTPUT)])
    print(f"Built {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
