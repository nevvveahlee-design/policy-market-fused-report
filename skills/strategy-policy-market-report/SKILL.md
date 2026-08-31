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

The strategic question and language captured in Workflow step 2 below are conversational context that shapes how steps 4-6 research and write — they do not add fields to this JSON contract.

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

If the host runs `scripts/run_report.py` to assemble the report mechanically
(rather than an LLM drafting the prose directly), it can optionally supply
`commercial_estimates` inside the `research` object — see
`scripts/report_schema.json` and "Commercial analysis rigor" below. This is
optional structured input for that fallback path; an LLM host writing prose
directly should just follow the rules in that section, not construct this
JSON shape by hand.

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
2. **Before researching, ask the user what strategic question this report
   should answer and what language to write it in.** Don't skip straight to
   a generic company overview — a report answering "should we expand into
   X" and a report answering "how exposed are we to competitor Y" need
   different research and a different Executive Summary/Recommendations
   focus, even for the same company. Offer a short menu to make this concrete,
   for example:
   - Overall competitive-position analysis (market standing, moat, growth trend)
   - A specific forward decision (e.g. "should this company enter/expand into <X>")
   - A deep dive on one business unit or product line
   - Something else — ask the user to describe it
   If the user has no preference, default to a general competitive-position
   read and match the language of the company name/request.
3. Select relevant methods from the bundled catalog.
4. Gather evidence once, covering both policy and commercial questions,
   scoped by the strategic question from step 2.
5. If the strategic question involves a market opportunity, a forward
   investment, or a go/no-go call, do the quantitative work required by
   "Commercial analysis rigor" below as part of this same pass — do not
   schedule a second research round for it.
6. Draft the Markdown report with the default sections, making sure the
   Executive Summary opens with one governing-thought sentence that answers
   the strategic question from step 2, and every later section either
   supports or qualifies that sentence rather than reading as a flat,
   unconnected survey.
7. Before finalizing, verify the headline number(s) the report's conclusion
   actually depends on, per "Verifying the headline numbers" below.
8. Render HTML or PDF only if the host can support the requested format.
9. If rendering is unavailable, return Markdown and a clear capability note instead of failing the report.

## Commercial analysis rigor

These rules apply only to `commercial_analysis` (and any decision-oriented
part of `executive_implications`/`recommendations` that rests on it) —
`policy_analysis` is unaffected and keeps working exactly as it does now:
select from the bundled method catalog, cite grounded evidence, close each
theme with a one-line "what this means for `<company>`" statement.

Most company reports stop at describing the market and the competition. If
the strategic question from Workflow step 2 is a market-sizing or forward
decision question, that isn't enough — build the estimate, don't just
narrate around it:

- **Size it bottom-up, not top-down.** Never hand over a single market-research
  firm's headline number as the answer. Build a short multiplication chain
  from the company/segment level up (population or account count ×
  penetration or adoption rate × price or spend per unit, adapted to
  whatever the category actually is). Then compare the result against any
  top-down figure you found in research as a *consistency check* — if they
  roughly agree, say so; if they disagree, say why instead of picking
  whichever is more convenient.
- **Validate the economics, don't assume them.** If margin, cost, or
  profitability is part of the answer, build a short buildup — the handful
  of cost/revenue components that actually drive it — ending in one clearly
  labeled result line, rather than a vague "margins look healthy" claim.
- **For a go/no-go or continue/scale call, run three scenarios** —
  conservative, base, optimistic — and sanity-check the base case against
  the bottom-up sizing above (note explicitly if it agrees "by construction"
  rather than as independent proof). **The conservative scenario must name
  the incumbent's most likely response** (a price cut, a fast-follow
  launch, a bundling move, a subsidy) and price it in — never model
  competitors as static. State a verdict (go / no-go / go-with-a-condition)
  and the condition that would flip it.
- **Label every assumption**, and call out explicitly which single
  assumption is load-bearing — the one that, if wrong, would flip the
  conclusion.
- **Never average two conflicting source numbers** to make them agree;
  reconcile them (explain the likely reason they differ) or pick the more
  defensible one and say why you did.
- **State the condition, if the claim is conditional** (a regulatory
  regime, a price floor, a churn assumption) — don't let a conditional
  claim read as an unconditional one.
- Quote the defensible number in the report, not the most flattering one.

If the strategic question is a straightforward competitive-position read
with no forward decision riding on it, a lighter qualitative commercial
section (as today) is fine — don't force a sizing exercise where nothing
in the request calls for one.

## Verifying the headline numbers

Before finalizing, take the 1-2 numbers the report's actual conclusion
depends on (the bottom-up SOM, the unit-economics result, or the
scenario-verdict number — whichever one the recommendation would fall apart
without) and verify them. Do **not** verify every minor figure in the
report — that cost isn't worth it; this is specifically about the number(s)
load-bearing enough that the whole conclusion rests on them.

- If the host supports spawning an independent agent (`spawn_agent`; see
  Portable tool mapping below), run a second pass: give it only the
  underlying evidence — not your derivation or your answer — and instruct
  it to independently re-derive the number and actively look for
  double-counting, unjustified optimism, or an assumption that doesn't
  hold up. Reconcile any discrepancy explicitly in the final report; do not
  silently keep whichever number you had first.
- If `spawn_agent` is unavailable, do this yourself as a distinct second
  pass: set the first derivation aside, re-derive the number again from the
  same evidence without looking at your first answer, then compare the two
  and reconcile any gap.
- Either way, this happens in the same session as the rest of the workflow
  — it is not a second research/search pass, only a second reasoning pass
  over evidence you already have.

## Portable tool mapping

Generic capability names and fallback rules live in [references/portability.md](references/portability.md).

| Capability | Expected use | Fallback |
| --- | --- | --- |
| `web_search` | Find current sources and evidence | Use supplied sources only, or ask for source material if no research source is available |
| `fetch` | Open a URL or retrieve source text | Use search snippets, pasted text, or user-provided documents |
| `write_file` | Save the report or rendered artifact | Return the Markdown report inline and note that file output is unavailable |
| `run_python` | Validate JSON/YAML and perform optional rendering checks | Skip optional rendering and validation steps, then deliver Markdown only |
| `spawn_agent` | Run an independent second pass to verify a headline commercial number | Re-derive the number yourself as a distinct second pass instead (see "Verifying the headline numbers") |

## Host capability rules

- Markdown is always the baseline deliverable.
- HTML and PDF are optional; do not block Markdown delivery when those tools are missing.
- If `web_search` or `fetch` is unavailable, do not fabricate current claims.
- If `write_file` is unavailable, do not stop the workflow; return the final Markdown in chat.
- If `run_python` is unavailable, skip structural validation and optional rendering checks only.
- If `spawn_agent` is unavailable, verify headline numbers yourself per "Verifying the headline numbers" instead of skipping verification.
