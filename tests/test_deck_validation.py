import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_MODULE_PATH = (
    ROOT / "skills" / "strategy-policy-market-report" / "scripts" / "build_deck.py"
)
VALIDATE_MODULE_PATH = (
    ROOT / "skills" / "strategy-policy-market-report" / "scripts" / "validate_deck.py"
)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def sample_report(**overrides):
    report = {
        "request": {
            "company": "Ningde Times 宁德时代",
            "business_unit": "Energy Storage",
            "geography": "China",
            "period": "2026",
            "output_format": "html",
        },
        "sections": {
            "executive_summary": (
                "The company should pace expansion carefully because policy pressure and market demand "
                "are both rising, but on different clocks."
            ),
            "scope_and_assumptions": "Company: Ningde Times 宁德时代\nGeography: China\nPeriod: 2026",
            "policy_analysis": (
                "This section summarizes policy evidence captured during the shared research pass.\n"
                "- New storage rules increase compliance overhead (Policy Watch; 2026-08-01; https://example.com/policy)"
            ),
            "commercial_analysis": (
                "This section summarizes commercial evidence captured during the shared research pass.\n"
                "- Utility-scale storage demand is growing quickly (Market Lens; 2026-08-05; https://example.com/market)"
            ),
            "integrated_implications": (
                "The integrated view compares regulatory and institutional pressure against market momentum."
            ),
            "recommendations": (
                "- Track the cited policy sources monthly.\n"
                "- Tie capital allocation decisions to the commercial evidence register."
            ),
            "methodology": (
                "The report uses one shared evidence pass and keeps policy-method grounding distinct "
                "from company-specific evidence."
            ),
            "sources": (
                "Policy evidence register:\n"
                "- Policy Watch | 2026-08-01 | https://example.com/policy\n\n"
                "Commercial evidence register:\n"
                "- Market Lens | 2026-08-05 | https://example.com/market"
            ),
        },
        "sources": [
            {
                "id": "policy-1",
                "category": "policy",
                "claim": "New storage rules increase compliance overhead.",
                "url": "https://example.com/policy",
                "date": "2026-08-01",
                "source_name": "Policy Watch",
            },
            {
                "id": "commercial-1",
                "category": "commercial",
                "claim": "Utility-scale storage demand is growing quickly.",
                "url": "https://example.com/market",
                "date": "2026-08-05",
                "source_name": "Market Lens",
            },
        ],
        "limitations": [],
        "rendering": {
            "requested_format": "html",
            "produced_format": "markdown",
            "markdown_only": True,
        },
        "markdown": "# Executive Summary\nBaseline markdown remains available.\n",
    }
    report.update(overrides)
    return report


def test_build_deck_writes_utf8_html_and_passes_validation(tmp_path):
    build_module = load_module(BUILD_MODULE_PATH, "build_deck")
    validate_module = load_module(VALIDATE_MODULE_PATH, "validate_deck")
    out_html = tmp_path / "deck.html"

    built_path = build_module.build_deck(sample_report(), out_html)

    assert built_path == out_html
    raw = out_html.read_bytes()
    decoded = raw.decode("utf-8")
    assert "宁德时代" in decoded
    assert '<meta charset="utf-8">' in decoded.lower()
    assert validate_module.validate_html(out_html) == []


def test_build_deck_escapes_html_sensitive_company_text(tmp_path):
    build_module = load_module(BUILD_MODULE_PATH, "build_deck")
    out_html = tmp_path / "deck.html"
    report = sample_report(
        request={
            "company": "A & B <Test> >",
            "business_unit": "Energy <Storage> & Grid",
            "geography": "U.S. > EU",
            "period": "2026 < 2027",
            "output_format": "html",
        }
    )

    build_module.build_deck(report, out_html)

    decoded = out_html.read_text(encoding="utf-8")
    assert "A &amp; B &lt;Test&gt; &gt;" in decoded
    assert "Energy &lt;Storage&gt; &amp; Grid" in decoded
    assert "U.S. &gt; EU" in decoded
    assert "2026 &lt; 2027" in decoded
    assert "<h1>A & B <Test> ></h1>" not in decoded


def test_validate_html_reports_unbalanced_divs_and_missing_headline(tmp_path):
    validate_module = load_module(VALIDATE_MODULE_PATH, "validate_deck")
    out_html = tmp_path / "broken.html"
    out_html.write_text(
        "<!doctype html><html><body><div class='slide'><div class='metric'><div class='n'>12%</div>"
        "<div class='l'>Growth</div></div></body></html>",
        encoding="utf-8",
    )

    errors = validate_module.validate_html(out_html)

    assert any("unbalanced <div>" in error for error in errors)
    assert any("missing headline" in error for error in errors)


def test_validate_html_reports_key_number_label_mismatch(tmp_path):
    validate_module = load_module(VALIDATE_MODULE_PATH, "validate_deck")
    out_html = tmp_path / "broken-metric.html"
    out_html.write_text(
        "<!doctype html><html><body><div class='slide'><h1>Headline</h1>"
        "<div class='hero'><div class='n'>12%</div></div></div></body></html>",
        encoding="utf-8",
    )

    errors = validate_module.validate_html(out_html)

    assert any("key-number labels" in error for error in errors)


def test_cli_reports_pdf_capability_note_when_chrome_is_unavailable(tmp_path):
    report_path = tmp_path / "report.json"
    out_html = tmp_path / "deck.html"
    out_pdf = tmp_path / "deck.pdf"
    report_path.write_text(json.dumps(sample_report()), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(BUILD_MODULE_PATH),
            "--report",
            str(report_path),
            "--out-html",
            str(out_html),
            "--out-pdf",
            str(out_pdf),
        ],
        check=False,
        capture_output=True,
        text=True,
        env={"PATH": ""},
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["html"] == str(out_html)
    assert payload["pdf"] is None
    assert "chrome" in payload["notes"][0].lower()
    assert out_html.exists()
    assert not out_pdf.exists()


def test_export_pdf_reports_failure_note_when_chrome_exists_but_export_fails(tmp_path, monkeypatch):
    build_module = load_module(BUILD_MODULE_PATH, "build_deck")
    html_path = tmp_path / "deck.html"
    pdf_path = tmp_path / "deck.pdf"
    html_path.write_text("<!doctype html><html><body>deck</body></html>", encoding="utf-8")

    monkeypatch.setattr(build_module, "detect_chrome", lambda: "chrome")

    class Completed:
        returncode = 1

    def fake_run(*args, **kwargs):
        return Completed()

    monkeypatch.setattr(build_module.subprocess, "run", fake_run)

    note = build_module.export_pdf(html_path, pdf_path)

    assert note == "Chrome/Chromium was available but PDF export failed; Markdown and HTML remain usable."
    assert not pdf_path.exists()
