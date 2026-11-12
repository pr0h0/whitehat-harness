// PreToolUse: keep network actions inside the engagement scope in .whitehat/scope.json.
// ponytail: string matching on shell commands is best-effort (variables, eval, scripts that
// open sockets themselves all slip past). The hard boundary is the sandbox network allowlist;
// this hook adds a readable reason, an audit trail and a deny that holds in every permission mode.
import { pathToFileURL } from "node:url";
import { audit, emit, loadScope, readInput, scopeExpired } from "./lib.mjs";

const NET_TOOLS =
  /(^|[\s;|&(`$])(curl|wget|http|https|nc|ncat|netcat|nmap|masscan|sqlmap|ffuf|gobuster|feroxbuster|dirb|nikto|nuclei|httpx|wfuzz|hydra|ssh|scp|sftp|telnet|ftp|rsync|socat)(\s|$)/;
const URL_RE = /\b[a-z][a-z0-9+.-]*:\/\/([^/\s'"`)]+)/gi;
const BARE_RE = /(?:^|[\s'"=@])((?:localhost|\d{1,3}(?:\.\d{1,3}){3}|\[[0-9a-f:]+\])(?::\d+)?)/gi;

const norm = (authority) => authority.replace(/^[^@]*@/, "").toLowerCase();

/** Hosts a tool call would talk to, as "host" or "host:port". */
export const targetsOf = (toolName, toolInput = {}) => {
  if (toolName === "Bash") {
    const cmd = String(toolInput.command ?? "");
    const out = new Set();
    for (const m of cmd.matchAll(URL_RE)) out.add(norm(m[1]));
    for (const m of cmd.matchAll(BARE_RE)) out.add(norm(m[1]));
    return { targets: [...out], network: NET_TOOLS.test(cmd) || out.size > 0 };
  }
  const urls = Object.values(toolInput).filter((v) => typeof v === "string" && /^[a-z][a-z0-9+.-]*:\/\//i.test(v));
  const targets = urls.map((u) => norm(u.split("://")[1].split(/[/?#]/)[0]));
  return { targets, network: targets.length > 0 };
};

const split = (hp) => {
  const m = hp.match(/^(\[[^\]]+\]|[^:]+)(?::(\d+))?$/);
  return m ? { host: m[1], port: m[2] ?? null } : { host: hp, port: null };
};
const LOOPBACK = new Set(["localhost", "127.0.0.1", "[::1]"]);

export const inScope = (target, hosts = []) => {
  const t = split(target);
  return hosts.some((entry) => {
    const e = split(String(entry).toLowerCase());
    const sameHost = e.host === t.host || (LOOPBACK.has(e.host) && LOOPBACK.has(t.host));
    return sameHost && (e.port === null || e.port === t.port);
  });
};

/** null = no opinion (normal permission flow continues), else a PreToolUse decision. */
export const decide = (input, scope) => {
  if (!scope) return null;
  const { targets, network } = targetsOf(input.tool_name, input.tool_input);
  if (!network) return null;
  const deny = (reason) => ({ permissionDecision: "deny", permissionDecisionReason: `[whitehat scope] ${reason}` });
  if (scope.invalid) return deny(`.whitehat/scope.json is not valid JSON (${scope.invalid}). Fix it before any network action.`);
  if (scopeExpired(scope)) return deny(`The engagement "${scope.engagement}" expired on ${scope.expires}. Renew the authorization and update scope.json.`);
  const out = targets.filter((t) => !inScope(t, scope.hosts));
  if (out.length)
    return deny(
      `${out.join(", ")} is outside the authorized scope (${(scope.hosts ?? []).join(", ") || "none"}). Do not retry with another tool or encoding; ask the user if the scope should change.`,
    );
  if (!targets.length)
    return {
      permissionDecision: "ask",
      permissionDecisionReason: "[whitehat scope] Network tool with no target the guard can read. Confirm the target is in scope.",
    };
  return null;
};

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const input = readInput();
  const scope = loadScope(input);
  const d = decide(input, scope);
  if (scope && (d || targetsOf(input.tool_name, input.tool_input).network))
    audit(input, {
      tool: input.tool_name,
      input: input.tool_name === "Bash" ? input.tool_input?.command : input.tool_input,
      decision: d?.permissionDecision ?? "pass",
    });
  if (d) emit({ hookSpecificOutput: { hookEventName: "PreToolUse", ...d } });
}
