"""Check that the report covers the original problem and has a readable PDF."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "paper" / "modeling_report.md"
PROBLEM = ROOT / "references" / "problem" / "TJMML_B.pdf"
PDF = ROOT / "output" / "pdf" / "modeling_report_draft.pdf"
REQUIRED_TEXT = [
    "CRITIC—TOPSIS 综合评价", "Kimi K3 优势与短板", "三类场景评价",
    "性能—成本与工程效率", "energy_data_available=False", "88.89%",
    "R^2=0.3147", "数据来源与可追溯性", "GLM-5.2 的同口径局部成绩",
]


def main() -> int:
    failures: list[str] = []
    if not PROBLEM.exists():
        failures.append("original problem PDF is missing")
    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    if not report_text:
        failures.append("Markdown report is missing")
    failures.extend(f"report marker is missing: {m}" for m in REQUIRED_TEXT if m not in report_text)
    if not PDF.exists() or PDF.stat().st_size < 100_000:
        failures.append("built PDF is missing or unexpectedly small")
    else:
        try:
            import fitz
            document = fitz.open(PDF)
            if len(document) < 8:
                failures.append(f"built PDF has too few pages: {len(document)}")
            extracted = "".join(page.get_text() for page in document)
            if "Kimi K3" not in extracted or "Pareto" not in extracted:
                failures.append("built PDF text extraction misses key content")
            document.close()
        except Exception as exc:
            failures.append(f"could not inspect built PDF: {exc}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("Paper validation passed: original, coverage markers, and PDF are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
