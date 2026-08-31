import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "strategy-policy-market-report" / "scripts" / "run_report.py"
SCHEMA_PATH = ROOT / "skills" / "strategy-policy-market-report" / "scripts" / "report_schema.json"


def load_module():
    spec = importlib.util.spec_from_file_location("run_report", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def sample_request(**overrides):
    request = {
        "company": "Acme Robotics",
        "business_unit": "Industrial Automation",
        "geography": "United States",
        "period": "2025-2026",
        "output_format": "markdown",
    }
    request.update(overrides)
    return request


def sample_research(**overrides):
    research = {
        "summary": "Shared evidence pass covering policy and commercial questions.",
        "policy_methods": [
            {
                "skill_id": "S000037",
                "name": "Technology Risk Gap Analysis",
                "rationale": "Useful for new-technology regulatory exposure.",
            }
        ],
        "policy_evidence": [
            {
                "id": "policy-1",
                "claim": "A draft safety rule would increase documentation burdens.",
                "url": "https://example.com/policy-rule",
                "date": "2026-08-01",
                "source_name": "Example Policy Agency",
            }
        ],
        "commercial_evidence": [
            {
                "id": "commercial-1",
                "claim": "Enterprise automation demand rose in the target segment.",
                "url": "https://example.com/market-demand",
                "date": "2026-07-15",
                "source_name": "Example Market Research",
            }
        ],
        "limitations": [],
    }
    research.update(overrides)
    return research


def assert_report_matches_schema_shape(report, schema):
    assert set(report) == set(schema["required"])
    assert isinstance(report["markdown"], str)

    request_properties = schema["properties"]["request"]["properties"]
    assert set(report["request"]) == set(request_properties)
    assert report["request"]["business_unit"] is None or isinstance(report["request"]["business_unit"], str)
    assert report["request"]["geography"] is None or isinstance(report["request"]["geography"], str)
    assert report["request"]["period"] is None or isinstance(report["request"]["period"], str)

    assert schema["properties"]["request"]["properties"]["business_unit"]["type"] == ["string", "null"]
    assert schema["properties"]["request"]["properties"]["geography"]["type"] == ["string", "null"]
    assert schema["properties"]["request"]["properties"]["period"]["type"] == ["string", "null"]

    section_properties = schema["properties"]["sections"]["properties"]
    assert set(report["sections"]) == set(section_properties)
    for value in report["sections"].values():
        assert isinstance(value, str)

    for source in report["sources"]:
        assert set(source) == {"id", "category", "claim", "url", "date", "source_name"}
        assert source["category"] in {"policy", "commercial"}
        assert isinstance(source["claim"], str)
        assert isinstance(source["url"], str)
        assert isinstance(source["date"], str)

    assert isinstance(report["limitations"], list)
    assert set(report["rendering"]) == {"requested_format", "produced_format", "markdown_only"}
    assert schema["properties"]["markdown"]["type"] == "string"


def test_validate_request_rejects_missing_company():
    module = load_module()

    errors = module.validate_request({"geography": "United States"})

    assert errors == ["company is required"]


def test_build_report_returns_required_sections_and_preserves_evidence_metadata():
    module = load_module()
    catalog = module.load_catalog(
        ROOT / "skills" / "strategy-policy-market-report" / "references" / "method-catalog.json"
    )

    report = module.build_report(sample_request(), sample_research(), catalog)

    expected_sections = {
        "executive_summary",
        "scope_and_assumptions",
        "policy_analysis",
        "commercial_analysis",
        "integrated_implications",
        "recommendations",
        "methodology",
        "sources",
    }
    assert set(report["sections"]) == expected_sections
    assert report["request"]["company"] == "Acme Robotics"
    assert report["sources"][0]["category"] == "policy"
    assert report["sources"][1]["category"] == "commercial"
    assert report["sources"][0]["url"] == "https://example.com/policy-rule"
    assert report["sources"][0]["date"] == "2026-08-01"
    assert report["sources"][1]["url"] == "https://example.com/market-demand"
    assert report["sources"][1]["date"] == "2026-07-15"
    assert "Technology Risk Gap Analysis" in report["sections"]["methodology"]
    assert "policy evidence" in report["sections"]["policy_analysis"].lower()
    assert "commercial evidence" in report["sections"]["commercial_analysis"].lower()


def test_build_report_records_no_web_limitations_when_research_is_unavailable():
    module = load_module()
    catalog = module.load_catalog(
        ROOT / "skills" / "strategy-policy-market-report" / "references" / "method-catalog.json"
    )
    research = sample_research(
        summary="No live web research was available in this run.",
        policy_evidence=[],
        commercial_evidence=[],
        limitations=["Live web research was unavailable; conclusions rely on provided inputs only."],
    )

    report = module.build_report(sample_request(), research, catalog)

    assert report["limitations"] == [
        "Live web research was unavailable; conclusions rely on provided inputs only."
    ]
    assert "Live web research was unavailable" in report["sections"]["sources"]
    assert "No policy evidence was available" in report["sections"]["policy_analysis"]
    assert "No commercial evidence was available" in report["sections"]["commercial_analysis"]


def test_build_report_rejects_unresolved_policy_method_names():
    module = load_module()
    catalog = module.load_catalog(
        ROOT / "skills" / "strategy-policy-market-report" / "references" / "method-catalog.json"
    )

    try:
        module.build_report(
            sample_request(),
            sample_research(policy_methods=[{"name": "Not In Catalog"}]),
            catalog,
        )
    except ValueError as exc:
        assert str(exc) == "unknown policy method: Not In Catalog"
    else:
        raise AssertionError("Expected unresolved policy method names to be rejected")


def test_build_report_rejects_malformed_sources():
    module = load_module()
    catalog = module.load_catalog(
        ROOT / "skills" / "strategy-policy-market-report" / "references" / "method-catalog.json"
    )

    try:
        module.build_report(
            sample_request(),
            sample_research(policy_evidence=[{"claim": "Missing source metadata"}]),
            catalog,
        )
    except ValueError as exc:
        assert str(exc) == "policy_evidence[0].url is required"
    else:
        raise AssertionError("Expected malformed source records to be rejected")


def test_build_report_matches_schema_shape_and_marks_markdown_only_rendering():
    module = load_module()
    schema = load_schema()
    catalog = module.load_catalog(
        ROOT / "skills" / "strategy-policy-market-report" / "references" / "method-catalog.json"
    )

    report = module.build_report(
        sample_request(output_format="html", business_unit=None, geography=None, period=None),
        sample_research(),
        catalog,
    )

    assert_report_matches_schema_shape(report, schema)
    assert report["rendering"] == {
        "requested_format": "html",
        "produced_format": "markdown",
        "markdown_only": True,
    }
    assert "HTML was requested" in report["limitations"][0]


def test_cli_writes_markdown_with_required_headings(tmp_path):
    request_path = tmp_path / "request.json"
    research_path = tmp_path / "research.json"
    output_path = tmp_path / "report.md"

    request_path.write_text(json.dumps(sample_request()), encoding="utf-8")
    research_path.write_text(json.dumps(sample_research()), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(MODULE_PATH), "--request", str(request_path), "--research", str(research_path), "--out", str(output_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    markdown = output_path.read_text(encoding="utf-8")
    assert "# Executive Summary" in markdown
    assert "# Scope And Assumptions" in markdown
    assert "# Policy Analysis" in markdown
    assert "# Commercial Analysis" in markdown
    assert "# Sources" in markdown
    assert "https://example.com/policy-rule" in markdown
    assert "2026-08-01" in markdown
    assert "https://example.com/market-demand" in markdown
    assert "2026-07-15" in markdown
