---
name: sast-triage
description: Run deterministic scanners (semgrep, and CodeQL if installed) and triage their results into candidate findings or documented false positives. Use when auditing a codebase or reviewing a branch, before or alongside manual tracing.
argument-hint: "[path or git ref to diff against]"
allowed-tools: Bash(semgrep *), Bash(codeql *), Bash(git diff *), Read, Grep, Glob
---

# Scanner run and triage

Scope: $ARGUMENTS (path, or a git ref: then only report results in files changed since it).

1. Run what is installed, saving raw output under `.whitehat/sast/`:
   - `semgrep scan --metrics=off --config ${CLAUDE_PLUGIN_ROOT}/rules --config p/default --json -o .whitehat/sast/semgrep.json <path>` (drop `p/default` if there is no network; it downloads the registry ruleset)
   - CodeQL only if `codeql` is on PATH and the code is open source or the user has a license: build a database and run the language's `security-extended` suite to SARIF.
   If neither is installed, say so and stop. Do not pretend to be a scanner.
2. Group results by rule and sink. Read the code for every group; never triage from the scanner message alone.
3. For each result decide one of:
   - **candidate**: the input is attacker-controlled and reaches the sink without an adequate defense. Write a finding file (template `${CLAUDE_PLUGIN_ROOT}/templates/finding.md`, `found_by: sast-triage`).
   - **false positive**: give the concrete reason (constant input, parameterized below, unreachable route) with `file:line`.
   - **needs trace**: the flow crosses too many files to judge quickly; list it for `/whitehat:trace`.
4. Write `.whitehat/sast/triage.md`: one table row per result group with the verdict and reason.
5. Report the counts (candidates, false positives, needs trace). Scanners miss whole bug classes such as broken access control and business logic, so say which entry points the scanners could not judge.

Dismissing a true positive is worse than keeping a false one. When unsure, choose "needs trace".
