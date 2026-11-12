// PostToolUse feedback: findings and failed checks both remain pending until a complete rescan.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, extname, join, relative } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { emit, loadState, projectDir, readInput, saveState } from "./lib.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SCANNED = new Set([".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".py", ".go", ".java", ".rb", ".php"]);

const run = (bin, args) => spawnSync(bin, args, {
  encoding: "utf8", timeout: 60_000, maxBuffer: 16 * 1024 * 1024,
});
const executionError = (r) => {
  if (r.error?.code === "ENOENT") return "not installed or executable not found; install it or configure its binary path";
  if (r.error) return `could not complete (${r.error.code || "process error"})`;
  if (r.signal) return `terminated by ${r.signal}`;
  if (r.status !== 0) return `exited with status ${r.status ?? "unknown"}`;
  return null;
};

/** Failed checks are not clean scans. Keep structured findings when available. */
export const semgrep = (file, execute = run) => {
  const bin = process.env.WHITEHAT_SEMGREP || "semgrep";
  const args = ["scan", "--json", "--quiet", "--metrics=off", "--config", join(ROOT, "rules")];
  if (process.env.WHITEHAT_SEMGREP_CONFIG) args.push("--config", process.env.WHITEHAT_SEMGREP_CONFIG);
  const r = execute(bin, [...args, file]);
  const error = executionError(r);
  if (r.error) return { error, findings: [] };
  try {
    const out = JSON.parse(r.stdout);
    if (!Array.isArray(out.results) || !Array.isArray(out.errors)) throw new Error("invalid schema");
    const findings = out.results.map((x) => ({
      tool: "semgrep", rule: x.check_id.split(".").pop(), line: x.start.line,
      severity: x.extra.severity, message: x.extra.message.trim(),
    }));
    const scanErrors = out.errors.length ? `${out.errors.length} scanner error(s); scan coverage is incomplete` : null;
    return { findings, ...(error || scanErrors ? { error: [error, scanErrors].filter(Boolean).join("; ") } : {}) };
  } catch {
    return { error: error || "invalid or missing JSON report", findings: [] };
  }
};

/** Gitleaks redacts findings; --exit-code 0 does not turn execution errors into success. */
export const gitleaks = (file, execute = run) => {
  const bin = process.env.WHITEHAT_GITLEAKS || "gitleaks";
  const r = execute(bin, ["dir", file, "--no-banner", "--redact", "--report-format", "json", "--report-path", "-", "--exit-code", "0"]);
  const error = executionError(r);
  if (r.error) return { error, findings: [] };
  try {
    const out = JSON.parse(r.stdout);
    if (!Array.isArray(out)) throw new Error("invalid schema");
    const findings = out.map((x) => {
      if (typeof x.RuleID !== "string" || typeof x.StartLine !== "number" || typeof x.Description !== "string") throw new Error("invalid finding");
      return { tool: "gitleaks", rule: x.RuleID, line: x.StartLine, severity: "ERROR", message: `${x.Description} (value redacted)` };
    });
    return { findings, ...(error ? { error } : {}) };
  } catch {
    return { error: error || "invalid or missing JSON report", findings: [] };
  }
};

export const format = (rel, findings) => [
  `whitehat edit gate: ${findings.length} finding(s) in ${rel}`,
  ...findings.map((f) => `- ${rel}:${f.line} [${f.tool}/${f.rule}] ${f.message}`), "",
  "Treat these as candidates, not facts. For each one: fix it, or state concretely why it is a false positive (what makes the input trusted or the sink safe).",
  "Do not add suppression comments or weaken the rule to make the warning go away.",
].join("\n");

export const reviewFile = (input, scanners = { semgrep, gitleaks }) => {
  const file = input.tool_input?.file_path;
  if (!file || !existsSync(file) || !SCANNED.has(extname(file))) return null;
  const rel = relative(projectDir(input), file);
  const results = Object.entries(scanners).map(([tool, scan]) => ({ tool, ...scan(file) }));
  const findings = results.flatMap((r) => r.findings);
  const errors = results.filter((r) => r.error).map((r) => `${r.tool}: ${r.error}`);
  const state = loadState(input);
  state.pending ??= {};
  if (findings.length || errors.length) {
    state.pending[rel] = {
      // A partial scan cannot clear a previous finding count.
      count: errors.length ? Math.max(findings.length, state.pending[rel]?.count ?? 0) : findings.length,
      session: input.session_id, ...(errors.length ? { errors } : {}),
    };
  } else delete state.pending[rel];
  saveState(input, state);
  const text = [
    findings.length ? format(rel, findings) : "",
    ...errors.map((e) => `whitehat: ${e}. ${rel} has NOT passed security checks; restore the scanner and rescan.`),
  ].filter(Boolean).join("\n\n");
  return text ? { hookSpecificOutput: { hookEventName: "PostToolUse", additionalContext: text } } : null;
};

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const output = reviewFile(readInput());
  if (output) emit(output);
}
