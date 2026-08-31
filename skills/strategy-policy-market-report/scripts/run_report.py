import argparse
import json
from pathlib import Path


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

ALLOWED_OUTPUT_FORMATS = {"markdown", "html", "pdf"}


def load_catalog(path):
    catalog_path = Path(path)
    raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    methods = raw if isinstance(raw, list) else raw.get("methods", [])
    by_name = {}
    for item in methods:
        for key in ("skill_id", "name", "canonical_name"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                by_name[value.strip().casefold()] = item
    return {
        "path": str(catalog_path),
        "methods": methods,
        "by_id": {item.get("skill_id"): item for item in methods if item.get("skill_id")},
        "by_name": by_name,
    }


def validate_request(request):
    errors = []
    if not isinstance(request, dict):
        return ["request must be an object"]
    company = request.get("company")
    if not isinstance(company, str) or not company.strip():
        errors.append("company is required")
    output_format = request.get("output_format", "markdown")
    if not isinstance(output_format, str) or output_format not in ALLOWED_OUTPUT_FORMATS:
        errors.append("output_format must be one of: markdown, html, pdf")
    for field in ("business_unit", "geography", "period"):
        value = request.get(field)
        if value is not None and not isinstance(value, str):
            errors.append(f"{field} must be a string")
    return errors


def _normalize_request(request):
    return {
        "company": request["company"].strip(),
        "business_unit": _clean_optional_text(request.get("business_unit")),
        "geography": _clean_optional_text(request.get("geography")),
        "period": _clean_optional_text(request.get("period")),
        "output_format": request.get("output_format", "markdown"),
    }


def _clean_optional_text(value):
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return value


def _normalize_research(research):
    if not isinstance(research, dict):
        raise ValueError("research must be an object")

    normalized = {
        "summary": _string_or_empty(research.get("summary")),
        "policy_methods": research.get("policy_methods", []),
        "policy_evidence": _normalize_evidence_list(research.get("policy_evidence", []), "policy"),
        "commercial_evidence": _normalize_evidence_list(
            research.get("commercial_evidence", []), "commercial"
        ),
        "limitations": _normalize_string_list(research.get("limitations", []), "limitations"),
    }

    if not isinstance(normalized["policy_methods"], list):
        raise ValueError("policy_methods must be a list")
    return normalized


def _string_or_empty(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    raise ValueError("summary must be a string")


def _normalize_string_list(values, field_name):
    if values is None:
        return []
    if not isinstance(values, list):
        raise ValueError(f"{field_name} must be a list")
    normalized = []
    for item in values:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field_name} entries must be non-empty strings")
        normalized.append(item.strip())
    return normalized


def _normalize_evidence_list(records, category):
    if records is None:
        return []
    if not isinstance(records, list):
        raise ValueError(f"{category}_evidence must be a list")

    normalized = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"{category}_evidence[{index}] must be an object")
        claim = record.get("claim")
        url = record.get("url")
        date = record.get("date")
        if not isinstance(claim, str) or not claim.strip():
            raise ValueError(f"{category}_evidence[{index}].claim is required")
        if not isinstance(url, str) or not url.strip():
            raise ValueError(f"{category}_evidence[{index}].url is required")
        if not isinstance(date, str) or not date.strip():
            raise ValueError(f"{category}_evidence[{index}].date is required")
        normalized.append(
            {
                "id": _clean_optional_text(record.get("id")) or f"{category}-{index + 1}",
                "category": category,
                "claim": claim.strip(),
                "url": url.strip(),
                "date": date.strip(),
                "source_name": _clean_optional_text(record.get("source_name")) or "Unknown source",
            }
        )
    return normalized


def build_report(request, research, catalog):
    errors = validate_request(request)
    if errors:
        raise ValueError("; ".join(errors))

    normalized_request = _normalize_request(request)
    normalized_research = _normalize_research(research)
    methods = _resolve_methods(normalized_research["policy_methods"], catalog)
    limitations = list(normalized_research["limitations"])
    rendering_limitations = _rendering_limitations(normalized_request["output_format"])
    limitations.extend(rendering_limitations)
    sources = normalized_research["policy_evidence"] + normalized_research["commercial_evidence"]

    sections = {
        "executive_summary": _build_executive_summary(normalized_request, normalized_research, methods),
        "scope_and_assumptions": _build_scope(normalized_request, normalized_research),
        "policy_analysis": _build_analysis_section(
            "policy",
            normalized_research["policy_evidence"],
            limitations,
        ),
        "commercial_analysis": _build_analysis_section(
            "commercial",
            normalized_research["commercial_evidence"],
            limitations,
        ),
        "integrated_implications": _build_integrated_implications(
            normalized_research["policy_evidence"],
            normalized_research["commercial_evidence"],
            limitations,
        ),
        "recommendations": _build_recommendations(
            normalized_request, normalized_research["policy_evidence"], normalized_research["commercial_evidence"]
        ),
        "methodology": _build_methodology(methods, normalized_research),
        "sources": _build_sources_section(sources, limitations),
    }

    report = {
        "request": normalized_request,
        "sections": sections,
        "sources": sources,
        "limitations": limitations,
        "rendering": {
            "requested_format": normalized_request["output_format"],
            "produced_format": "markdown",
            "markdown_only": True,
        },
    }
    report["markdown"] = render_markdown(report)
    return report


def _resolve_methods(policy_methods, catalog):
    resolved = []
    seen = set()
    for index, item in enumerate(policy_methods):
        if not isinstance(item, dict):
            raise ValueError(f"policy_methods[{index}] must be an object")
        skill_id = _clean_optional_text(item.get("skill_id"))
        name = _clean_optional_text(item.get("name"))
        rationale = _clean_optional_text(item.get("rationale"))
        catalog_entry = None
        if skill_id:
            catalog_entry = catalog.get("by_id", {}).get(skill_id)
            if catalog_entry is None:
                raise ValueError(f"unknown policy method: {skill_id}")
        elif name:
            catalog_entry = catalog.get("by_name", {}).get(name.casefold())
            if catalog_entry is None:
                raise ValueError(f"unknown policy method: {name}")
        else:
            raise ValueError(f"policy_methods[{index}] must include a known skill_id or name")
        resolved_name = (
            (catalog_entry or {}).get("canonical_name")
            or (catalog_entry or {}).get("name")
            or name
        )
        unique_key = skill_id or resolved_name
        if unique_key in seen:
            continue
        seen.add(unique_key)
        resolved.append(
            {
                "skill_id": skill_id or catalog_entry.get("skill_id"),
                "name": resolved_name,
                "rationale": rationale,
            }
        )
    return resolved


def _rendering_limitations(requested_format):
    if requested_format == "markdown":
        return []
    upper = requested_format.upper()
    return [
        f"{upper} was requested, but this runner only produces Markdown in Task 3; no {upper} artifact was generated."
    ]


def _build_executive_summary(request, research, methods):
    method_names = ", ".join(method["name"] for method in methods) or "catalog-grounded policy methods"
    policy_count = len(research["policy_evidence"])
    commercial_count = len(research["commercial_evidence"])
    return (
        f"This report assesses {request['company']} using one shared research pass and separates "
        f"policy risk from commercial opportunity. It grounds the policy line in {method_names} and "
        f"draws on {policy_count} policy evidence item(s) and {commercial_count} commercial evidence item(s)."
    )


def _build_scope(request, research):
    scope_parts = [f"Company: {request['company']}"]
    if request.get("business_unit"):
        scope_parts.append(f"Business unit: {request['business_unit']}")
    if request.get("geography"):
        scope_parts.append(f"Geography: {request['geography']}")
    if request.get("period"):
        scope_parts.append(f"Period: {request['period']}")
    if research["summary"]:
        scope_parts.append(f"Research scope: {research['summary']}")
    return "\n".join(scope_parts)


def _build_analysis_section(category, evidence_items, limitations):
    label = f"{category} evidence"
    if not evidence_items:
        limitation_note = ""
        if limitations:
            limitation_note = " Limitations: " + " ".join(limitations)
        return f"No {label} was available for this run.{limitation_note}"

    lines = [f"This section summarizes {label} captured during the shared research pass."]
    for item in evidence_items:
        lines.append(
            f"- {item['claim']} ({item['source_name']}; {item['date']}; {item['url']})"
        )
    return "\n".join(lines)


def _build_integrated_implications(policy_evidence, commercial_evidence, limitations):
    if not policy_evidence and not commercial_evidence:
        base = "Integrated implications remain provisional because neither policy nor commercial evidence was available."
        if limitations:
            base += " " + " ".join(limitations)
        return base
    return (
        "The integrated view compares regulatory and institutional pressure against market momentum so the "
        "company can see where policy shifts could accelerate, delay, or redirect commercial outcomes."
    )


def _build_recommendations(request, policy_evidence, commercial_evidence):
    actions = [
        f"Prioritize actions that keep {request['company']} prepared for the policy scenarios cited above.",
        "Separate near-term commercial bets from assumptions that still require fresh validation.",
    ]
    if policy_evidence:
        actions.append("Assign an owner to track the cited policy sources and update the implications when dates or rules change.")
    if commercial_evidence:
        actions.append("Tie go-to-market and investment decisions to the commercial evidence register rather than to uncited assumptions.")
    return "\n".join(f"- {item}" for item in actions)


def _build_methodology(methods, research):
    lines = ["The report uses one shared evidence pass and keeps policy-method grounding distinct from company-specific evidence."]
    if methods:
        lines.append("Selected policy methods:")
        for method in methods:
            detail = method["name"]
            if method.get("skill_id"):
                detail += f" ({method['skill_id']})"
            if method.get("rationale"):
                detail += f": {method['rationale']}"
            lines.append(f"- {detail}")
    else:
        lines.append("No policy methods were explicitly selected for this run.")
    if research["limitations"]:
        lines.append("Recorded limitations:")
        for limitation in research["limitations"]:
            lines.append(f"- {limitation}")
    return "\n".join(lines)


def _build_sources_section(sources, limitations):
    lines = ["Policy evidence register:"]
    policy_sources = [item for item in sources if item["category"] == "policy"]
    commercial_sources = [item for item in sources if item["category"] == "commercial"]

    if policy_sources:
        for item in policy_sources:
            lines.append(f"- {item['source_name']} | {item['date']} | {item['url']}")
    else:
        lines.append("- No policy evidence was available.")

    lines.append("")
    lines.append("Commercial evidence register:")
    if commercial_sources:
        for item in commercial_sources:
            lines.append(f"- {item['source_name']} | {item['date']} | {item['url']}")
    else:
        lines.append("- No commercial evidence was available.")

    if limitations:
        lines.append("")
        lines.append("Limitations:")
        for limitation in limitations:
            lines.append(f"- {limitation}")
    return "\n".join(lines)


def render_markdown(report):
    lines = []
    for key in REQUIRED_SECTION_KEYS:
        lines.append(f"# {_heading_for_key(key)}")
        lines.append(report["sections"][key])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _heading_for_key(key):
    return key.replace("_", " ").title()


def _load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Build a provider-neutral strategy report.")
    parser.add_argument("--request", required=True, help="Path to the normalized request JSON file.")
    parser.add_argument("--research", required=True, help="Path to the research JSON file.")
    parser.add_argument("--out", required=True, help="Path to the Markdown output file.")
    args = parser.parse_args()

    request = _load_json(args.request)
    research = _load_json(args.research)
    catalog_path = Path(__file__).resolve().parents[1] / "references" / "method-catalog.json"
    catalog = load_catalog(catalog_path)
    report = build_report(request, research, catalog)
    Path(args.out).write_text(report["markdown"], encoding="utf-8")


if __name__ == "__main__":
    main()
