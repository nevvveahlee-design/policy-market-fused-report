# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


ASSET_DIR = Path(__file__).resolve().parents[1] / "assets"
if str(ASSET_DIR) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR))

import deck_engine as engine


REQUIRED_SECTION_KEYS = (
    "executive_summary",
    "scope_and_assumptions",
    "policy_analysis",
    "commercial_analysis",
    "integrated_implications",
    "recommendations",
    "methodology",
    "sources",
)


def build_deck(report: dict, out_html: Path) -> Path:
    _validate_report(report)
    request = report["request"]
    sections = report["sections"]
    sources = report.get("sources", [])
    engine.BRAND = _brand_line(request)

    slides = [
        engine.cover(
            request["company"],
            "Unified strategy report with optional HTML/PDF rendering",
        ),
        engine.answer_slide(
            "Executive summary",
            _deck_line(request),
            sections["executive_summary"],
            _pillar_metrics(report),
            2,
        ),
        engine.prose_slide(
            "Analysis",
            _deck_line(request),
            [
                ("Scope and assumptions", sections["scope_and_assumptions"]),
                ("Policy analysis", sections["policy_analysis"]),
                ("Commercial analysis", sections["commercial_analysis"]),
                ("Integrated implications", sections["integrated_implications"]),
            ],
            3,
        ),
        engine.prose_slide(
            "Recommendations and methodology",
            _deck_line(request),
            [
                ("Recommendations", sections["recommendations"]),
                ("Methodology", sections["methodology"]),
                ("Limitations", _limitations_text(report.get("limitations", []))),
                ("Markdown baseline", "Markdown remains the baseline artifact even when deck export is unavailable."),
            ],
            4,
        ),
        engine.sources_slide("Sources", _deck_line(request), sources, 5),
    ]
    return engine.render(slides, Path(out_html))


def _validate_report(report: dict) -> None:
    if not isinstance(report, dict):
        raise ValueError("report must be an object")
    for key in ("request", "sections", "markdown"):
        if key not in report:
            raise ValueError(f"report is missing required key: {key}")
    if not isinstance(report["request"], dict):
        raise ValueError("report.request must be an object")
    if not isinstance(report["sections"], dict):
        raise ValueError("report.sections must be an object")
    for key in REQUIRED_SECTION_KEYS:
        value = report["sections"].get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"report.sections.{key} must be a non-empty string")


def _brand_line(request: dict) -> str:
    parts = [request["company"]]
    for field in ("business_unit", "geography", "period"):
        value = request.get(field)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())
    parts.append("Strategy Policy Market Report")
    return " | ".join(parts)


def _deck_line(request: dict) -> str:
    parts = []
    for field in ("business_unit", "geography", "period"):
        value = request.get(field)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())
    return " | ".join(parts) or "Company-wide scope"


def _pillar_metrics(report: dict) -> list[dict]:
    policy_sources = sum(1 for item in report.get("sources", []) if item.get("category") == "policy")
    commercial_sources = sum(
        1 for item in report.get("sources", []) if item.get("category") == "commercial"
    )
    limitations = report.get("limitations", [])
    return [
        {
            "metric": str(policy_sources),
            "label": "Policy sources",
            "title": "Institutional line is evidence-backed",
            "support": "Structured policy evidence remains separated from commercial support.",
        },
        {
            "metric": str(commercial_sources),
            "label": "Commercial sources",
            "title": "Market line is evidence-backed",
            "support": "Commercial claims remain tied to dated source records.",
        },
        {
            "metric": str(len(limitations)),
            "label": "Limitations",
            "title": "Capability limits stay explicit",
            "support": "Optional rendering failures do not invalidate the Markdown report.",
        },
        {
            "metric": str(len(report.get("sections", {}))),
            "label": "Sections rendered",
            "title": "Deck mirrors the normalized report contract",
            "support": "The wrapper consumes the existing Task 3 report object without changing it.",
        },
    ]


def _limitations_text(limitations: list[str]) -> str:
    if not limitations:
        return "No additional limitations were recorded for this run."
    return "\n".join(f"- {item}" for item in limitations)


def detect_chrome() -> str | None:
    candidates = [
        "chrome",
        "google-chrome",
        "chromium",
        "chromium-browser",
        "msedge",
    ]
    for name in candidates:
        found = shutil.which(name)
        if found:
            return found
    return None


def export_pdf(html_path: Path, pdf_path: Path) -> str | None:
    chrome = detect_chrome()
    if chrome is None:
        return "Chrome/Chromium was not available; skipped optional PDF export."

    completed = subprocess.run(
        [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            str(html_path.resolve()),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return "Chrome/Chromium was available but PDF export failed; Markdown and HTML remain usable."
    return None


def _load_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the optional HTML/PDF deck artifact.")
    parser.add_argument("--report", required=True, help="Path to the normalized report JSON file.")
    parser.add_argument("--out-html", required=True, help="Path to the HTML deck output file.")
    parser.add_argument("--out-pdf", help="Optional PDF output path.")
    args = parser.parse_args()

    report = _load_json(Path(args.report))
    html_path = build_deck(report, Path(args.out_html))
    pdf_path = None
    notes = []

    if args.out_pdf:
        note = export_pdf(html_path, Path(args.out_pdf))
        if note is None:
            pdf_path = str(Path(args.out_pdf))
        else:
            notes.append(note)

    payload = {
        "html": str(html_path),
        "pdf": pdf_path,
        "notes": notes,
        "markdown_only": False,
    }
    json.dump(payload, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
