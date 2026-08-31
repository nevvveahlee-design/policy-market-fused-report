---
name: strategy-policy-market-report
description: Use when a user asks for a company analysis, policy-risk report, market or competitive brief, regulatory assessment, or executive strategy deck, especially when they provide a company name or want Markdown, HTML, or PDF output.
---

# Strategy Policy Market Report

## Overview

Produce one provider-neutral company report that combines policy-risk and commercial/market analysis. Markdown is the baseline output; HTML and PDF are optional renderings when the host can support them.

## Trigger and minimum input

Use this skill when the request is about a company, business unit, product, geography, or time window and the user wants analysis, recommendations, or a board-ready report.

Minimum input:

```json
{"company":"Acme Corp"}
```

Optional fields:

- `business_unit`
- `geography`
- `period`
- `output_format` (`markdown` by default; `html` and `pdf` are optional extensions)

If `company` is missing, ask only for that field before proceeding.

## Request contract

The downstream report runner consumes a normalized request object with these fields:

```json
{
  "company": "Acme Corp",
  "business_unit": "Enterprise",
  "geography": "United States",
  "period": "last 12 months",
  "output_format": "markdown"
}
```

Field rules:

- `company` is required.
- `business_unit`, `geography`, and `period` are optional scope refinements.
- `output_format` is optional and defaults to `markdown`.

## Report contract

The generated report is a structured object with these top-level fields:

```json
{
  "request": {},
  "sections": {},
  "sources": [],
  "limitations": [],
  "rendering": {}
}
```

Required section keys under `sections`:

- `executive_summary`
- `scope_and_assumptions`
- `policy_analysis`
- `commercial_analysis`
- `integrated_implications`
- `recommendations`
- `methodology`
- `sources`

Section rules:

- Every section key must exist, even if the section body is brief.
- `sources` contains the evidence register used by the report.
- `limitations` records any missing research or rendering capability.
- `rendering` records the requested format and whether only Markdown was produced.

## Output contract

Default report sections:

1. Executive summary
2. Scope and assumptions
3. Policy analysis
4. Commercial analysis
5. Integrated implications
6. Recommendations
7. Methodology
8. Sources

## Evidence rules

- Use one research pass for both policy and commercial questions.
- Never invent policy methods outside the bundled catalog.
- Company-specific claims require captured source URLs and dates.
- Keep policy-method grounding separate from company-specific evidence.
- If live research is unavailable, say so and separate user-provided facts from unverified assumptions.
- Do not imply affiliation with McKinsey or any external brand.

## Workflow

1. Confirm the company and any optional scope fields.
2. Select relevant methods from the bundled catalog.
3. Gather evidence once, covering both policy and commercial questions.
4. Draft the Markdown report with the default sections.
5. Render HTML or PDF only if the host can support the requested format.
6. If rendering is unavailable, return Markdown and a clear capability note instead of failing the report.

## Portable tool mapping

Generic capability names and fallback rules live in [references/portability.md](references/portability.md).

| Capability | Expected use | Fallback |
| --- | --- | --- |
| `web_search` | Find current sources and evidence | Use supplied sources only, or ask for source material if no research source is available |
| `fetch` | Open a URL or retrieve source text | Use search snippets, pasted text, or user-provided documents |
| `write_file` | Save the report or rendered artifact | Return the Markdown report inline and note that file output is unavailable |
| `run_python` | Validate JSON/YAML and perform optional rendering checks | Skip optional rendering and validation steps, then deliver Markdown only |

## Host capability rules

- Markdown is always the baseline deliverable.
- HTML and PDF are optional; do not block Markdown delivery when those tools are missing.
- If `web_search` or `fetch` is unavailable, do not fabricate current claims.
- If `write_file` is unavailable, do not stop the workflow; return the final Markdown in chat.
- If `run_python` is unavailable, skip structural validation and optional rendering checks only.
