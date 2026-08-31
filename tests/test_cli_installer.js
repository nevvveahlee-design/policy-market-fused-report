const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const ROOT = path.resolve(__dirname, "..");
const CLI = path.join(ROOT, "bin", "cli.js");

function runInstallerSmokeTest() {
  const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "strategy-policy-market-report-"));

  try {
    const result = spawnSync(process.execPath, [CLI, "--project"], {
      cwd: tempRoot,
      encoding: "utf8",
    });

    assert.strictEqual(result.status, 0, result.stderr || result.stdout);

    const skillsRoot = path.join(tempRoot, ".claude", "skills");
    const installedSkill = path.join(skillsRoot, "strategy-policy-market-report");

    assert.ok(fs.existsSync(installedSkill), "expected unified skill to be installed");
    assert.ok(
      fs.existsSync(path.join(installedSkill, "SKILL.md")),
      "expected SKILL.md in installed skill",
    );
    assert.ok(
      fs.existsSync(path.join(installedSkill, "references", "method-catalog.json")),
      "expected canonical method catalog in installed skill",
    );
    assert.ok(
      fs.existsSync(path.join(installedSkill, "scripts", "run_report.py")),
      "expected report runner in installed skill",
    );
    assert.ok(
      fs.existsSync(path.join(installedSkill, "assets", "deck_engine.py")),
      "expected deck engine in installed skill",
    );

    assert.ok(
      !fs.existsSync(path.join(skillsRoot, "policy-market-fused-report")),
      "legacy fused-report skill should not be installed",
    );
    assert.ok(
      !fs.existsSync(path.join(skillsRoot, "mckinsey-deck")),
      "legacy deck skill should not be installed",
    );
  } finally {
    fs.rmSync(tempRoot, { recursive: true, force: true });
  }
}

runInstallerSmokeTest();
