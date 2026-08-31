# Portability

This package uses generic capability names so the skill can run on different hosts without naming vendor-specific tools.

## Capability map

| Generic capability | What it covers | If the host does not provide it |
| --- | --- | --- |
| `web_search` | Search the web for current policy, market, company, and regulatory sources | Proceed with user-provided sources only, or ask for source material if the report would otherwise need live evidence |
| `fetch` | Open a URL, page, or document and extract the source text | Use search snippets, pasted excerpts, or uploaded documents instead |
| `write_file` | Save the Markdown report or rendered artifact to disk | Return the Markdown report inline and clearly note that file output is unavailable |
| `run_python` | Parse JSON/YAML, validate structure, and run optional HTML/PDF checks | Skip optional validation and rendering, then deliver Markdown only |

## Fallback rules

- Markdown is the required baseline output on every host.
- HTML and PDF are optional extensions, never a requirement for a successful run.
- If live research is unavailable, say so and separate user-provided facts from unverified assumptions.
- If a requested capability is missing, continue with the strongest safe fallback instead of inventing a tool name or fabricating results.
- Never imply the host must be a specific AI vendor, browser, or shell environment.

## Host behavior summary

1. If the host can search or fetch, use those capabilities for evidence gathering.
2. If the host can write files, save the report artifact after generation.
3. If the host can run Python, use it for validation and optional rendering checks.
4. If any of those capabilities are absent, return Markdown and a note describing the missing capability.

