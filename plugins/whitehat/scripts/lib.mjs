// Shared helpers for whitehat hooks. Node >= 18, no dependencies.
import { appendFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

export const readInput = () => {
  try {
    return JSON.parse(readFileSync(0, "utf8") || "{}");
  } catch {
    return {};
  }
};

export const projectDir = (input) => process.env.CLAUDE_PROJECT_DIR || input.cwd || process.cwd();
export const stateDir = (input) => join(projectDir(input), ".whitehat");

/** The engagement file. No file = no engagement = the scope guard stays out of the way. */
export const loadScope = (input) => {
  const p = join(stateDir(input), "scope.json");
  if (!existsSync(p)) return null;
  try {
    return JSON.parse(readFileSync(p, "utf8"));
  } catch (e) {
    return { invalid: String(e.message) };
  }
};

export const scopeExpired = (scope, now = new Date()) =>
  Boolean(scope?.expires) && new Date(`${scope.expires}T23:59:59Z`) < now;

const statePath = (input) => join(stateDir(input), "state.json");
export const loadState = (input) => {
  try {
    return JSON.parse(readFileSync(statePath(input), "utf8"));
  } catch {
    return { pending: {} };
  }
};
export const saveState = (input, state) => {
  mkdirSync(stateDir(input), { recursive: true });
  writeFileSync(statePath(input), `${JSON.stringify(state, null, 2)}\n`);
};

/** Append-only evidence trail of every network-relevant action the agent attempted. */
export const audit = (input, entry) => {
  try {
    mkdirSync(stateDir(input), { recursive: true });
    appendFileSync(
      join(stateDir(input), "audit.jsonl"),
      `${JSON.stringify({ ts: new Date().toISOString(), session: input.session_id, ...entry })}\n`,
    );
  } catch {
    // auditing must never break the agent
  }
};

export const emit = (obj) => {
  process.stdout.write(JSON.stringify(obj));
  process.exit(0);
};
