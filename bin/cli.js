#!/usr/bin/env node
/**
 * [INPUT]: node:fs/path/os; package's own skills/ directory
 * [OUTPUT]: installs strategy-policy-market-report into ~/.claude/skills/
 *           (default) or ./.claude/skills/ (--project)
 * [POS]: the package's only entry point -- npx policy-market-fused-report installs it
 */
const fs = require("fs");
const path = require("path");
const os = require("os");

const SKILLS = ["strategy-policy-market-report"];
const SRC = path.join(__dirname, "..", "skills");

const args = process.argv.slice(2);
if (args.includes("--help") || args.includes("-h")) {
  console.log(`
policy-market-fused-report -- install the unified strategy-policy-market-report skill

Usage:
  npx policy-market-fused-report            install to ~/.claude/skills/   (global, recommended)
  npx policy-market-fused-report --project  install to ./.claude/skills/   (this project only)

Installs one canonical skill:
  strategy-policy-market-report -- provider-neutral company analysis workflow

After installing, ask your agent:
  Create a strategy policy market report for <company>
`);
  process.exit(0);
}

const dest = args.includes("--project")
  ? path.join(process.cwd(), ".claude", "skills")
  : path.join(os.homedir(), ".claude", "skills");

fs.mkdirSync(dest, { recursive: true });

for (const name of SKILLS) {
  const from = path.join(SRC, name);
  const to = path.join(dest, name);
  const existed = fs.existsSync(to);
  fs.cpSync(from, to, { recursive: true });
  console.log(`  ${existed ? "↻ updated" : "✓ installed"}  ${name} → ${to}`);
}

console.log(`
Done. The unified skill is in place.

Ask your agent:
  Create a strategy policy market report for <company>

Markdown is the baseline output. HTML and PDF are optional renderings when
your host supports Python and Chrome/Chromium. Live research uses your own
agent/runtime capabilities and may be unavailable in some environments.
`);
