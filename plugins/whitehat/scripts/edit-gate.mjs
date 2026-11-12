// PostToolUse on Edit|Write|MultiEdit: scan the file the agent just wrote and hand findings back
// to the agent as context. PostToolUse cannot undo the write; the Stop gate holds the turn open
// until the file scans clean or the agent explains why a finding is a false positive.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, extname, join, relative } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { emit, loadState, projectDir, readInput, saveState } from "./lib.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SCANNED = new Set([".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".py", ".go", ".java", ".rb", ".php"]);

const run = (bin, args) => {
  const r = spawnSync(bin, args, { encoding: "utf8", timeout: 60_000, maxBuffer: 16 * 1024 * 1024 });
  return r.error ? null : r;
};

/** Semgrep with the bundled rules (plus WHITEHAT_SEMGREP_CONFIG, e.g. "p/default", if set). */
export const semgrep = (file) => {
  const bin = process.env.WHITEHAT_SEMGREP || "semgrep";
  const args = ["scan", "--json", "--quiet", "--metrics=off", "--config", join(ROOT, "rules")];
  if (process.env.WHITEHAT_SEMGREP_CONFIG) args.push("--config", process.env.WHITEHAT_SEMGREP_CONFIG);
  const r = run(bin, [...args, file]);
  if (!r) return { missing: true, findings: [] };
  try {
    const out = JSON.parse(r.stdout);
    return {
      findings: out.results.map((x) => ({
        tool: "semgrep",
        rule: x.check_id.split(".").pop(),
        line: x.start.line,
        severity: x.extra.severity,
        message: x.extra.message.trim(),
      })),
    };
  } catch {
    return { error: (r.stderr || "semgrep produced no JSON").slice(0, 300), findings: [] };
  }
};

/** gitleaks on just this file, secrets redacted in the output. */
export const gitleaks = (file) => {
  const bin = process.env.WHITEHAT_GITLEAKS || "gitleaks";
  const r = run(bin, ["dir", file, "--no-banner", "--redact", "--report-format", "json", "--report-path", "-", "--exit-code", "0"]);
  if (!r) return { missing: true, findings: [] };
  try {
    return {
      findings: JSON.parse(r.stdout || "[]").map((x) => ({
        tool: "gitleaks",
        rule: x.RuleID,
        line: x.StartLine,
        severity: "ERROR",
        message: `${x.Description} (value redacted)`,
      })),
    };
  } catch {
    return { findings: [] };
  }
};

export const format = (rel, findings) =>
  [
    `whitehat edit gate: ${findings.length} finding(s) in ${rel}`,
    ...findings.map((f) => `- ${rel}:${f.line} [${f.tool}/${f.rule}] ${f.message}`),
    "",
    "Treat these as candidates, not facts. For each one: fix it, or state concretely why it is a false positive (what makes the input trusted or the sink safe).",
    "Do not add suppression comments or weaken the rule to make the warning go away.",
  ].join("\n");

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const input = readInput();
  const file = input.tool_input?.file_path;
  if (!file || !existsSync(file) || !SCANNED.has(extname(file))) process.exit(0);
  const rel = relative(projectDir(input), file);
  const sg = semgrep(file);
  const gl = gitleaks(file);
  const findings = [...sg.findings, ...gl.findings];
  const state = loadState(input);
  const notes = [];
  if (sg.missing && !state.warnedMissing) {
    notes.push("whitehat: semgrep is not installed, so edits are only checked for secrets. Install it (pipx install semgrep) to enable code checks.");
    state.warnedMissing = true;
  }
  if (sg.error) notes.push(`whitehat: semgrep failed: ${sg.error}`);
  if (findings.length) state.pending[rel] = { count: findings.length, session: input.session_id };
  else delete state.pending[rel];
  saveState(input, state);
  const text = [findings.length ? format(rel, findings) : "", ...notes].filter(Boolean).join("\n\n");
  if (text) emit({ hookSpecificOutput: { hookEventName: "PostToolUse", additionalContext: text } });
}
