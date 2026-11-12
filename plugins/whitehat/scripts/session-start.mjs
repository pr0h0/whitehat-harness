// SessionStart: when an engagement is active, put the scope in front of the agent.
import { pathToFileURL } from "node:url";
import { emit, loadScope, readInput, scopeExpired } from "./lib.mjs";

export const context = (scope) => {
  if (!scope) return null;
  if (scope.invalid) return "whitehat: .whitehat/scope.json is invalid JSON. All network actions will be denied until it is fixed.";
  const lines = [
    `whitehat engagement "${scope.engagement}" is active (authorized by ${scope.authorizedBy ?? "unknown"}, expires ${scope.expires ?? "never"}).`,
    `In-scope hosts: ${(scope.hosts ?? []).join(", ") || "none"}. Anything else is out of scope and will be denied.`,
  ];
  if (scope.rules?.length) lines.push(`Rules of engagement: ${scope.rules.join("; ")}.`);
  if (scopeExpired(scope)) lines.push("The engagement has EXPIRED. Do not run any network action.");
  return lines.join("\n");
};

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const c = context(loadScope(readInput()));
  if (c) emit({ hookSpecificOutput: { hookEventName: "SessionStart", additionalContext: c } });
}
