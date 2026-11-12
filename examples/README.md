# Example settings

`settings.json` is a starting point for `.claude/settings.json` in a project where you run security work. A plugin can't ship these rules, so you add them yourself:

- `permissions.deny` keeps the agent's file tools away from secrets.
- `sandbox` puts shell commands in an OS sandbox with network access limited to the listed hosts. With `failIfUnavailable`, the sandbox refuses to start instead of quietly running unsandboxed. With `allowUnsandboxedCommands: false`, the agent can't ask to step outside it.

Check it on your own machine before you rely on it:

1. Run `/sandbox` to confirm the sandbox is active. On Linux it needs `bubblewrap` and `socat`.
2. Ask the agent to `curl` an in-scope URL. It should work.
3. Ask it to `curl` any other host. It should fail.

The sandbox covers shell commands only. Claude's own file tools, MCP servers and hooks run outside it. See https://code.claude.com/docs/en/sandboxing.
