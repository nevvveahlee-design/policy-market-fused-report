# Unified Strategy Analysis Skill Design

## Goal

Replace the two separate skill entrypoints with one independently branded,
portable GitHub skill. A user should be able to enter a request such as
“produce an analysis report on Company X” and receive a complete policy-risk
and commercial/market report, optionally rendered as an executive HTML/PDF
deck. The implementation may reuse authorized source material, but the
public-facing workflow, naming, interfaces, and documentation will be unified
and rewritten for this project.

## Recommended architecture

The canonical public contract will be a provider-neutral `SKILL.md` plus
portable reference data and scripts. It will not depend on Claude-only tool
names, proprietary SDKs, or a sibling skill. A small compatibility section will
map generic capabilities such as web search, file writing, and shell execution
to the host AI product's available tools.

The skill will route a request through four internal stages:

1. Scope the company, flagship business, geography, time horizon, and desired
   deliverable.
2. Select relevant policy methods from the bundled catalog and run one shared
   evidence-gathering pass covering both policy and commercial questions.
3. Produce two linked narratives: institutional/policy risk and commercial
   opportunity, with separate evidence standards and explicit source tracking.
4. Render the result as HTML and, when the environment supports it, PDF; run
   structural and visual quality checks before delivery.

The rendering implementation will live behind a project-owned wrapper/module so
the skill does not refer to a sibling skill. Existing rendering primitives may
be adapted under the stated authorization, with a stable internal interface for
cover, summary, prose, charts, tables, and sources.

## Directory shape

```text
skills/<new-skill-name>/
  SKILL.md                       # canonical provider-neutral instructions
  README.md                      # GitHub installation and usage
  LICENSE
  THIRD_PARTY_NOTICES.md
  agents/openai.yaml
  references/
    method-catalog.json
    evidence.json
    rendering.md
    portability.md               # host capability fallbacks
  scripts/
    build_deck.py
    validate_deck.py
    run_report.py                 # optional CLI entrypoint for host wrappers
  assets/
    deck_engine.py
```

The user-facing trigger should be broad enough to catch requests for company
analysis, business reports, policy analysis, market research, regulatory risk,
or strategy decks. When the company or business scope is missing, the skill
asks for only the minimum clarification needed; otherwise it proceeds
automatically. The default output is a complete Markdown report with an
executive summary, scope/assumptions, policy analysis, commercial analysis,
integrated implications, recommendations, methodology, and source register.
HTML/PDF is an optional second output when the host can run the renderer.

The existing installer will install only the unified skill by default. A
compatibility alias may be retained temporarily if it does not create a second
source of truth; otherwise the old skill folders will be removed only after
their callers and package metadata are updated.

## Behavior and boundaries

- Never invent policy methods outside the bundled catalog.
- Use one research pass for both analysis lines.
- Keep company-specific claims tied to captured source URLs and dates.
- Keep policy-method grounding distinct from company-specific evidence.
- Use action-oriented conclusions rather than exposing internal method labels in
  the main narrative.
- Treat PDF export as optional when Chrome or PDF tooling is unavailable, and
  report the missing capability clearly.
- Normalize all generated HTML writes to UTF-8, including Windows execution.
- Make Markdown the baseline interoperable output; treat HTML/PDF as optional
  renderings rather than the only successful result.
- Never require a particular AI vendor's tool names. If live web research is
  unavailable, state that limitation and separate user-provided facts from
  unverified assumptions instead of fabricating current claims.
- Do not present the output as affiliated with McKinsey or another external
  brand; use project-owned naming and neutral consulting-style language.

## Compatibility and migration

The package CLI will keep its current installation contract unless a breaking
change is necessary. The new skill becomes the only canonical implementation.
README examples, package metadata, installer paths, and notices will be updated
to reference the unified name. Any legacy directory retained for migration will
contain only a redirect/compatibility note and no duplicated workflow.

## Verification

Before delivery, verify:

- skill frontmatter and directory naming with the bundled quick validator;
- installer output into a temporary target;
- JSON references parse successfully;
- the build script runs on a minimal fixture;
- generated HTML has balanced `div` tags and UTF-8 content;
- PDF page count and basic link annotations are present when PDF tooling is
  available;
- no README, package, or installer path still points to the old canonical
  sibling-skill workflow.
- a clean-host smoke test can invoke the skill with a company name and obtain a
  Markdown report without vendor-specific setup;
- the report contains both analysis lines, citations/source records, and an
  explicit limitation note when web access is unavailable.

## Licensing record

The implementation will rely on the user's stated authorization covering
modification, merging, rewriting, attribution treatment, GitHub distribution,
commercial use, sublicensing, and derivative works. The repository should keep
an internal record of that authorization. Public licensing language must not
claim broader rights than the authorization grants.

## Out of scope

- Adding new research sources or expanding the policy catalog;
- building a hosted service or GitHub Actions deployment;
- guaranteeing identical tool behavior across every AI product; portability
  means a provider-neutral contract with documented capability fallbacks;
- changing the analysis domain beyond policy risk, market analysis, and deck
  generation;
- creating visual assets unrelated to the report/deck workflow.
