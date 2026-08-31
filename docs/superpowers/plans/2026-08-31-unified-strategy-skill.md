# Unified Strategy Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish one provider-neutral GitHub skill that turns a company-analysis request into a complete policy + commercial Markdown report, with optional HTML/PDF rendering.

**Architecture:** Replace the two public skill entrypoints with one canonical skill. Keep the policy catalog/evidence as data, expose a provider-neutral workflow, and put rendering behind a project-owned Python module with Markdown as the portable fallback.

**Tech Stack:** Markdown, JSON, Node.js CLI, Python 3, existing deck rendering primitives, shell-based validation.

## Global Constraints

- Markdown is the baseline interoperable output; HTML/PDF are optional renderings.
- Use one research pass for both analysis lines.
- Never invent policy methods outside the bundled catalog.
- Company-specific claims require captured source URLs and dates.
- Never require vendor-specific AI tool names.
- Do not imply affiliation with McKinsey or another external brand.
- Normalize generated HTML writes to UTF-8.

---

### Task 1: Define the canonical skill package

**Files:**
- Create: `skills/strategy-policy-market-report/SKILL.md`
- Create: `skills/strategy-policy-market-report/agents/openai.yaml`
- Create: `skills/strategy-policy-market-report/references/portability.md`

**Interfaces:**
- Produces the canonical trigger, workflow, input schema, output schema, and host capability fallback rules used by later tasks.

- [ ] **Step 1: Write the skill contract**

Document the trigger phrase, minimum input (`company`), optional fields (`business_unit`, `geography`, `period`, `output_format`), default Markdown sections, evidence rules, and fallback behavior.

- [ ] **Step 2: Add portable tool mappings**

Document generic capabilities (`web_search`, `fetch`, `write_file`, `run_python`) and how the host should proceed when each is unavailable.

- [ ] **Step 3: Validate frontmatter and invocation metadata**

Run the bundled skill validator against `skills/strategy-policy-market-report` and fix naming/frontmatter errors.

### Task 2: Consolidate reference data

**Files:**
- Create: `skills/strategy-policy-market-report/references/method-catalog.json`
- Create: `skills/strategy-policy-market-report/references/evidence.json`
- Modify: `skills/policy-market-fused-report/references/skills.json`
- Modify: `skills/policy-market-fused-report/references/evidence.json`

**Interfaces:**
- `method-catalog.json` and `evidence.json` become the canonical data files; report generation reads them without sibling-skill paths.

- [ ] **Step 1: Add a JSON migration check**

Create a small command that parses both source files, compares record counts and IDs, and fails if any record is lost or duplicated.

- [ ] **Step 2: Copy and normalize the canonical data**

Move the data into the unified skill reference directory without changing evidence content; normalize only keys needed by the new reader.

- [ ] **Step 3: Run the migration check**

Verify the unified files contain the same 25 methods and all evidence records as the source catalog.

### Task 3: Build the provider-neutral report runner

**Files:**
- Create: `skills/strategy-policy-market-report/scripts/run_report.py`
- Create: `skills/strategy-policy-market-report/scripts/report_schema.json`
- Create: `tests/test_report_contract.py`

**Interfaces:**
- `load_catalog(path) -> dict`
- `validate_request(request) -> list[str]`
- `build_report(request, research, catalog) -> dict`
- CLI: `python run_report.py --request request.json --research research.json --out report.md`

- [ ] **Step 1: Write failing contract tests**

Cover missing company rejection, required section generation, source URL preservation, separation of policy and commercial evidence, and explicit no-web limitation output.

- [ ] **Step 2: Implement request and research validation**

Accept JSON so any AI host can create the input artifact, validate required fields, and reject malformed sources without making network assumptions.

- [ ] **Step 3: Implement Markdown generation**

Generate executive summary, scope, policy analysis, commercial analysis, integrated implications, recommendations, methodology, and sources. Preserve source URL/date fields in the output.

- [ ] **Step 4: Run focused tests**

Run `pytest tests/test_report_contract.py -q` and confirm all contract tests pass.

### Task 4: Integrate optional HTML/PDF rendering

**Files:**
- Create: `skills/strategy-policy-market-report/assets/deck_engine.py`
- Create: `skills/strategy-policy-market-report/scripts/build_deck.py`
- Create: `skills/strategy-policy-market-report/scripts/validate_deck.py`
- Create: `tests/test_deck_validation.py`

**Interfaces:**
- `build_deck(report: dict, out_html: Path) -> Path`
- `validate_html(path: Path) -> list[str]`
- CLI must return a successful Markdown-only result when browser/PDF tools are absent.

- [ ] **Step 1: Write failing renderer validation tests**

Test UTF-8 output, balanced div tags, required headline/key-number consistency, and graceful omission of PDF when Chrome is unavailable.

- [ ] **Step 2: Adapt the authorized rendering implementation**

Place the unified engine under the new skill, remove sibling-skill imports/paths, and ensure all file writes specify UTF-8.

- [ ] **Step 3: Implement the optional build wrapper**

Read the normalized report object, render HTML when requested, detect Chrome/PDF availability, and emit a clear capability note instead of failing the baseline report.

- [ ] **Step 4: Run renderer tests**

Run `pytest tests/test_deck_validation.py -q` and validate a fixture HTML output.

### Task 5: Replace installer and repository documentation

**Files:**
- Modify: `bin/cli.js`
- Modify: `package.json`
- Modify: `README.md`
- Modify: `THIRD_PARTY_NOTICES.md`
- Create: `LICENSE` or update the project license only after confirming the stated authorization scope.

**Interfaces:**
- CLI installs the unified skill as the only canonical package and does not install duplicate sibling workflows.

- [ ] **Step 1: Write installer smoke checks**

Exercise the CLI against a temporary install directory and assert the unified `SKILL.md`, references, scripts, and assets are present.

- [ ] **Step 2: Update installer paths and package metadata**

Replace old skill path assumptions and preserve the existing command-line contract where possible.

- [ ] **Step 3: Rewrite README usage**

Document the one-line company request, Markdown baseline, optional HTML/PDF, provider-neutral usage, and capability limitations.

- [ ] **Step 4: Run installer smoke checks**

Verify no installed path points to the old sibling-skill workflow.

### Task 6: End-to-end verification and GitHub release readiness

**Files:**
- Create: `tests/fixtures/company-request.json`
- Create: `tests/fixtures/research.json`
- Create: `scripts/verify_release.ps1`

**Interfaces:**
- `verify_release.ps1` runs validation, tests, JSON checks, installer smoke test, and stale-reference scan with nonzero exit on failure.

- [ ] **Step 1: Create deterministic fixtures**

Use fictional company data and explicit source URLs so tests do not require live web access.

- [ ] **Step 2: Run the complete verification script**

Confirm skill validation, Python tests, JSON parsing, Markdown generation, optional deck checks, and stale-reference scan pass.

- [ ] **Step 3: Inspect release contents**

Confirm the GitHub tree contains the unified skill, README, license/notices, tests, and no accidental generated report artifacts.

- [ ] **Step 4: Commit coherent milestones**

Commit each completed task separately when Git metadata is available; if the current directory remains outside a Git repository, report that release commits must be created after repository initialization.

## Self-review

The plan covers the portability contract, canonical data migration, Markdown baseline, optional rendering, installer migration, documentation, and release verification. It does not promise identical behavior across every AI product; it defines a provider-neutral contract with explicit fallbacks. No placeholder steps or undefined cross-task interfaces remain.
