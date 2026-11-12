import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { test } from "node:test";
import { gitleaks, reviewFile, semgrep } from "../plugins/whitehat/scripts/edit-gate.mjs";
import { decide as stop } from "../plugins/whitehat/scripts/stop-gate.mjs";

const response = (value, status = 0) => ({ status, stdout: JSON.stringify(value), stderr: "" });
const clean = () => ({ findings: [] });
const missing = () => ({ error: "not installed", findings: [] });
const sgFinding = { check_id: "test.sql", start: { line: 1 }, extra: { severity: "ERROR", message: "unsafe SQL" } };

for (const [name, scan, empty] of [["semgrep", semgrep, { results: [], errors: [] }], ["gitleaks", gitleaks, []]]) {
  test(`${name}: missing executable, timeout, signal and nonzero exit are failures`, () => {
    for (const r of [
      { error: { code: "ENOENT" } }, { error: { code: "ETIMEDOUT" } },
      { ...response(empty), status: null, signal: "SIGTERM" }, response(empty, 2),
    ]) assert.ok(scan("fixture.js", () => r).error);
  });
  test(`${name}: malformed, empty and wrong-shape reports are failures`, () => {
    for (const stdout of ["", "not json", "null", "{}", '{"results":[]}']) {
      assert.ok(scan("fixture.js", () => ({ status: 0, stdout })).error);
    }
  });
  test(`${name}: successful empty report is clean`, () => {
    assert.deepEqual(scan("fixture.js", () => response(empty)), { findings: [] });
  });
}

test("semgrep: JSON errors with exit zero are failed checks, even alongside findings", () => {
  const result = semgrep("fixture.js", () => response({ results: [sgFinding], errors: [{ type: "ParseError" }] }));
  assert.equal(result.findings.length, 1);
  assert.match(result.error, /incomplete/);
});

test("gitleaks: findings never copy secret values into feedback", () => {
  const result = gitleaks("fixture.js", () => response([{ RuleID: "test", StartLine: 1, Description: "fake fixture", Secret: "DO-NOT-PRINT" }]));
  assert.equal(result.findings.length, 1);
  assert.doesNotMatch(JSON.stringify(result), /DO-NOT-PRINT/);
  assert.match(result.findings[0].message, /redacted/);
});

test("pending findings survive scanner failure and clear only after a complete clean rescan", () => {
  const cwd = mkdtempSync(join(tmpdir(), "whitehat-edit-"));
  try {
    const file = join(cwd, "fixture.js");
    writeFileSync(file, "export const fixture = 1;\n");
    const input = { cwd, session_id: "current", tool_input: { file_path: file } };
    const state = () => JSON.parse(readFileSync(join(cwd, ".whitehat/state.json"), "utf8"));
    reviewFile(input, { semgrep: () => ({ findings: [{ rule: "sql", line: 1, tool: "semgrep", message: "unsafe" }] }), gitleaks: clean });
    const warning = reviewFile(input, { semgrep: missing, gitleaks: clean });
    assert.match(warning.hookSpecificOutput.additionalContext, /semgrep.*not installed/);
    assert.equal(state().pending["fixture.js"].count, 1);
    assert.equal(state().pending["fixture.js"].errors.length, 1);
    assert.match(stop(input, state()).reason, /1 failed check/);
    const glWarning = reviewFile(input, { semgrep: clean, gitleaks: missing });
    assert.match(glWarning.hookSpecificOutput.additionalContext, /gitleaks.*not installed/);
    assert.ok(state().pending["fixture.js"]);
    assert.equal(reviewFile(input, { semgrep: clean, gitleaks: clean }), null);
    assert.deepEqual(state().pending, {});
  } finally { rmSync(cwd, { recursive: true, force: true }); }
});

test("failure without findings creates pending state in the current session", () => {
  const cwd = mkdtempSync(join(tmpdir(), "whitehat-error-"));
  try {
    const file = join(cwd, "fixture.js"); writeFileSync(file, "const x = 1;\n");
    const input = { cwd, session_id: "new", tool_input: { file_path: file } };
    reviewFile(input, { semgrep: clean, gitleaks: missing });
    const state = JSON.parse(readFileSync(join(cwd, ".whitehat/state.json"), "utf8"));
    assert.equal(state.pending["fixture.js"].count, 0);
    assert.equal(state.pending["fixture.js"].session, "new");
    assert.equal(stop(input, state).decision, "block");
  } finally { rmSync(cwd, { recursive: true, force: true }); }
});

test("actual hook process reports both missing binaries and retains pending errors", () => {
  const cwd = mkdtempSync(join(tmpdir(), "whitehat-process-"));
  try {
    const file = join(cwd, "fixture.js"); writeFileSync(file, "const x = 1;\n");
    const result = spawnSync(process.execPath, ["plugins/whitehat/scripts/edit-gate.mjs"], {
      input: JSON.stringify({ cwd, session_id: "process", tool_input: { file_path: file } }), encoding: "utf8",
      env: { ...process.env, CLAUDE_PROJECT_DIR: cwd, WHITEHAT_SEMGREP: join(cwd, "missing-semgrep"), WHITEHAT_GITLEAKS: join(cwd, "missing-gitleaks") },
    });
    assert.equal(result.status, 0, result.stderr);
    const feedback = JSON.parse(result.stdout).hookSpecificOutput.additionalContext;
    assert.match(feedback, /semgrep: not installed/); assert.match(feedback, /gitleaks: not installed/);
    const state = JSON.parse(readFileSync(join(cwd, ".whitehat/state.json"), "utf8"));
    assert.equal(state.pending["fixture.js"].errors.length, 2);
  } finally { rmSync(cwd, { recursive: true, force: true }); }
});
