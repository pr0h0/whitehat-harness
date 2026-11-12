# whitehat-harness

A Claude Code plugin for **authorized** security work: code audits, pentests of systems you are allowed to test, and security gates that check code while an agent writes it.

It does three things:

1. **Scope guard.** A `PreToolUse` hook denies Bash, WebFetch and MCP calls aimed at hosts outside your engagement scope, and logs every network action to `.whitehat/audit.jsonl`.
2. **Edit gate.** A `PostToolUse` hook runs Semgrep (bundled rules) and gitleaks on every file the agent writes, and feeds the findings back to the agent. A `Stop` hook blocks completion once to request fixes or explanations; it does not enforce a protected merge.
3. **Audit and pentest skills.** Seven skills turn a security review into repeatable steps that write files you can diff, review and report on, instead of chat history.

## Install

You need Claude Code, plus Node.js 18 or newer, which the hooks run on.

```text
/plugin marketplace add pr0h0/whitehat-harness
/plugin install whitehat@whitehat-harness
```

Or, from a shell, per project:

```bash
claude plugin marketplace add pr0h0/whitehat-harness
claude plugin install whitehat@whitehat-harness --scope project
```

Install both scanners before relying on the edit gate (a missing scanner is reported as a failed check):

```bash
pipx install semgrep          # or: pip install semgrep
# gitleaks: https://github.com/gitleaks/gitleaks#installing
```

To try it without installing: `claude --plugin-dir ./plugins/whitehat`.

## Skills

| Skill | What it does | Writes |
|---|---|---|
| `/whitehat:scope` | Records who authorized the test, which hosts are in scope, and until when | `.whitehat/scope.json` |
| `/whitehat:recon` | Maps entry points, auth, sinks and hotspots of a codebase (read-only subagent) | `.whitehat/recon.md` |
| `/whitehat:trace <target>` | Follows untrusted input from one entry point to its sinks | `.whitehat/findings/F-*.md` (candidates) |
| `/whitehat:sast-triage` | Runs Semgrep (and CodeQL if present) and triages each result | `.whitehat/sast/` |
| `/whitehat:verify <id>` | A skeptic subagent tries to disprove a finding, and confirms it only with a failing test or an in-scope request | updates the finding |
| `/whitehat:pentest-recon <url>` | Maps the attack surface of a running app inside scope, no payloads | `.whitehat/surface.md` |
| `/whitehat:report` | Builds a report from confirmed findings only | `.whitehat/report.md` |

A finding moves `candidate -> confirmed | rejected`. Only `/whitehat:verify` can confirm a finding, and only with evidence it produced. The format is in [`templates/finding.md`](plugins/whitehat/templates/finding.md).

## Typical flows

**Code audit**

```text
/whitehat:recon
/whitehat:sast-triage
/whitehat:trace POST /rest/user/login
/whitehat:verify F-001
/whitehat:report
```

**Pentest of a lab target**, e.g. OWASP Juice Shop on your own machine:

```bash
docker run --rm -p 127.0.0.1:3000:3000 bkimminich/juice-shop
```

```text
/whitehat:scope juice-shop-local
/whitehat:pentest-recon http://localhost:3000
/whitehat:verify F-001
```

**Developer gate.** Install the plugin and keep working. When the agent writes code that matches a rule, it receives the finding right away. Missing scanners, failed processes, malformed reports and Semgrep-reported errors remain pending rather than counting as clean scans. Only a complete successful rescan with no findings clears the file. The Stop hook blocks once to request action; use a required CI check for merge enforcement.

## Configuration

| Variable | Effect |
|---|---|
| `WHITEHAT_SEMGREP_CONFIG` | Extra Semgrep config, e.g. `p/default` (downloads the registry ruleset) |
| `WHITEHAT_SEMGREP`, `WHITEHAT_GITLEAKS` | Paths to the binaries if they are not on `PATH` |
| `WHITEHAT_STOP_GATE=0` | Turn off the Stop gate. Findings are still reported. |

The scope guard does nothing until `.whitehat/scope.json` exists, so it stays out of normal development work. See [`templates/scope.example.json`](plugins/whitehat/templates/scope.example.json).

Add `.whitehat/` to `.gitignore`. The audit log and the findings can contain sensitive data.

## What this does not do

Read this before relying on it:

- **The scope guard is a seatbelt, not a wall.** It reads command text. A variable (`curl $T`) makes it ask you to confirm. A script that opens its own sockets gets past it. For a hard boundary, also turn on Claude Code's sandbox with a network allowlist, and run untrusted work in a container or VM. [`examples/settings.json`](examples/settings.json) has a starting point.
- **Plugins cannot set permissions.** Claude Code does not let a plugin ship `permissions` rules, so deny rules (for example, never read `.env`) have to go in your own settings. Use the example file.
- **The edit gate is pattern matching.** The bundled rules catch common injection sinks in JS/TS. They do not find broken access control, business logic flaws, or anything that needs data flow across files. That is what `/whitehat:trace` and a human are for.
- **Model output is not evidence.** A finding is real only when a test or a request shows it. This plugin is built around that rule. Keep to it when you write reports.
- **Authorized use only.** Only test systems you own, or systems you have written permission to test.

## Development

```bash
npm test                                  # hook unit tests (node --test)
claude plugin validate .                  # marketplace + plugin manifests
claude --plugin-dir ./plugins/whitehat    # load it locally
```

## License

MIT
