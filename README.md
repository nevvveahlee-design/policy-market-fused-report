# policy-market-fused-report

This package keeps the existing `npx policy-market-fused-report` install command, but it now installs one canonical skill: `skills/strategy-policy-market-report/`.

The unified skill is provider-neutral in its workflow and output contract:

- Minimum input is a company name.
- Markdown is the baseline deliverable.
- HTML and PDF are optional renderings when the host can run the bundled Python helpers and has Chrome or Chromium available.
- Live research depends on the host's search and fetch capabilities; when they are unavailable, the skill falls back to a clearly limited Markdown report instead of fabricating current claims.

## Install

```bash
npx policy-market-fused-report
npx policy-market-fused-report --project
```

The command-line contract stays the same:

- default install target: `~/.claude/skills/`
- project install target: `./.claude/skills/`

The installed skill directory is:

```text
strategy-policy-market-report
```

Restart your host application after install if it caches local skill directories.

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

If optional rendering is unavailable, the skill should still return the Markdown report and record the limitation explicitly.

## What Gets Installed

The installer copies only:

```text
skills/strategy-policy-market-report/
```

That package contains:

- `SKILL.md`: the canonical workflow contract
- `references/`: bundled method catalog, evidence, and portability guidance
- `scripts/run_report.py`: Markdown report generator
- `scripts/build_deck.py`: optional HTML/PDF wrapper
- `assets/deck_engine.py`: project-owned deck rendering primitives

## Provider-Neutral Contract

The skill is written so an AI host can map its own capabilities onto a small generic set:

- `web_search`
- `fetch`
- `write_file`
- `run_python`

See `skills/strategy-policy-market-report/references/portability.md` for the host capability mapping in the repository copy. If a host lacks one or more capabilities, the fallback is to preserve the Markdown workflow and note the limitation rather than fail the task.

## Repository Layout

```text
bin/cli.js
skills/strategy-policy-market-report/
tests/test_cli_installer.js
tests/test_report_contract.py
tests/test_deck_validation.py
```

`skills/strategy-policy-market-report/` is the only skill package in this
repository — everything under it, including `assets/deck_engine.py`, is
original work.

## Licensing

MIT — see `LICENSE`.
