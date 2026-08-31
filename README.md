# policy-market-fused-report

Give this skill a company name and it produces one report combining two
independently-evidenced lines of analysis: a **policy/institutional-risk**
read (grounded in a bundled library of real government/institutional
analysis methods) and a **commercial/market** read (market sizing,
competitive positioning, source-tiered evidence). One shared research pass
covers both; the output is Markdown by default, with optional HTML/PDF
rendering.

**This is a [Claude Code](https://claude.com/claude-code) skill.** The
automated install below only works there — see "Don't have Claude Code?"
further down if you're on a different AI tool.

- Minimum input: a company name.
- Markdown is always the baseline deliverable — never blocked by missing
  optional capabilities.
- HTML and PDF are optional renderings, produced when the host can run the
  bundled Python helpers and has Chrome/Chromium available.
- One live research pass covers both the policy and commercial angle —
  never a duplicated second search.
- Company-specific claims require a captured source URL and date; the
  bundled policy-method catalog is never extended with invented methods.
- If live research is unavailable, the skill says so explicitly rather than
  fabricating current claims.

## Install

This package is **not published to the npm registry** — `npx
policy-market-fused-report` only resolves if you run it from inside a local
clone of this repo. Running it from anywhere else fails with a 404.

```bash
git clone https://github.com/nevvveahlee-design/policy-market-fused-report.git
cd policy-market-fused-report
npx policy-market-fused-report            # installs to ~/.claude/skills/ (all projects)
npx policy-market-fused-report --project  # installs to ./.claude/skills/ (current project only)
```

The installed skill directory is:

```text
strategy-policy-market-report
```

**Restart Claude Code after installing** — it only picks up new skills on
startup, not mid-session.

## Don't have Claude Code?

The `npx` install command only works if you have Claude Code (or another
tool that reads `.claude/skills/`) — it just copies files into that folder,
which nothing else looks at.

If you're using ChatGPT, Gemini, or another AI tool instead:

1. Open `skills/strategy-policy-market-report/SKILL.md` in this repo and
   copy its content into that tool's custom instructions / system prompt.
2. If the tool supports file uploads, also attach
   `skills/strategy-policy-market-report/references/method-catalog.json`
   and `evidence.json` as reference material.
3. Trigger it by describing what you want in plain language, the same way
   you would with Claude Code — you'll just need to paste the instructions
   in again each new conversation, since there's no persistent "skill"
   mechanism outside Claude Code.

Optional HTML/PDF rendering (`scripts/build_deck.py`) still needs an
environment that can run Python and, for PDF, has Chrome/Chromium — most
chat-only AI tools can't do this themselves. Markdown output will still
work anywhere the AI can follow written instructions.

## Use

Once installed, ask your agent for a company report in plain language, for example:

> Create a strategy policy market report for BYD

You can optionally specify scope fields that map to the skill's request contract:

```json
{
  "company": "BYD",
  "business_unit": "Passenger Vehicles",
  "geography": "Europe",
  "period": "last 12 months",
  "output_format": "markdown"
}
```

Supported output behavior:

- `markdown`: always the baseline
- `html`: optional rendering when Python-based deck generation is available
- `pdf`: optional rendering when HTML generation is available and Chrome/Chromium can export PDF

If optional rendering is unavailable, the skill still returns the Markdown
report and records the limitation explicitly instead of failing.

## What Gets Installed

The installer copies only:

```text
skills/strategy-policy-market-report/
```

That package contains:

- `SKILL.md` — the canonical workflow contract
- `references/` — bundled method catalog, evidence, and portability guidance
- `scripts/run_report.py` — Markdown report generator
- `scripts/build_deck.py` — optional HTML/PDF wrapper
- `scripts/validate_deck.py` — structural QC for rendered decks
- `assets/deck_engine.py` — project-owned deck rendering primitives
- `agents/openai.yaml` — a compatibility manifest for OpenAI-style hosts

## Provider-Neutral Contract

The skill's workflow logic is written so an AI host can map its own
capabilities onto a small generic set, rather than hard-coding a specific
vendor's tool names:

- `web_search`
- `fetch`
- `write_file`
- `run_python`

See `skills/strategy-policy-market-report/references/portability.md` for
the full host-capability mapping and fallback rules. If a host lacks one or
more capabilities, the fallback is to preserve the Markdown workflow and
note the limitation rather than fail the task.

## Repository Layout

```text
bin/cli.js                            installer (see Install above)
skills/strategy-policy-market-report/ the only skill package — original work
tests/                                pytest + node test suite
docs/superpowers/                     the implementation plan and design spec
```

## Testing

```bash
python -m pytest -q tests/
node tests/test_cli_installer.js
```

## Licensing

MIT — see `LICENSE`.
