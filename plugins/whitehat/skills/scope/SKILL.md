---
name: scope
description: Create or update the engagement scope (.whitehat/scope.json) that the whitehat scope guard enforces. Use before any pentest or network testing, or when the user says what they are authorized to test.
argument-hint: "[engagement name]"
disable-model-invocation: true
---

# Set the engagement scope

The scope file is what the PreToolUse scope guard enforces. Writing it is a statement that the user is authorized to test those hosts, so the facts must come from the user, never from you.

1. Ask the user, in one message, for anything they have not already given:
   - engagement name
   - who authorized the testing (themselves, for a lab on their own machine, or the asset owner named in a written authorization)
   - the exact hosts in scope, as `host` or `host:port`
   - an expiry date (YYYY-MM-DD)
   - any rules of engagement (forbidden techniques, rate limits, testing windows)
2. If the user cannot name who authorized the testing, stop. Do not write a scope file. Explain that the plugin is for authorized testing only.
3. Never add a host the user did not name. Do not widen `example.com` to `*.example.com` yourself.
4. Write `.whitehat/scope.json` in the project root, following `${CLAUDE_PLUGIN_ROOT}/templates/scope.example.json`.
5. Add `.whitehat/` to `.gitignore` if it is not there. The audit log and findings can contain sensitive data.
6. Show the user the file and tell them:
   - every Bash/WebFetch/MCP call that targets a host outside the list will be denied, and logged to `.whitehat/audit.jsonl`
   - the guard reads command text, so it is a seatbelt, not a wall: for a hard boundary also enable the sandbox with a network allowlist (`/sandbox`, and `sandbox.network.allowedDomains` in settings)
