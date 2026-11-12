---
name: trace
description: Trace untrusted input from one entry point (or to one sink class) through the code and record candidate findings in .whitehat/findings/. Use after recon, for a specific route, hotspot or vulnerability class.
argument-hint: "<entry point, hotspot or vuln class, e.g. 'POST /rest/user/login' or 'sql'>"
---

# Source-to-sink trace

Target: $ARGUMENTS

If no target was given, read `.whitehat/recon.md` and ask which hotspot to trace. Depth beats breadth: one entry point traced properly is worth more than twenty guessed.

For each path from an attacker-controlled source to a dangerous sink:

1. Write down every hop with `file:line`: where the value enters, each function it passes through, each transformation, and the sink. Open every file you cite.
2. At each hop ask: is the value validated, encoded, parameterized or type-checked here? Is it the right defense for this sink? A check for the wrong context (HTML-escaping before SQL, substring allowlists for URLs) does not count.
3. Ask who can reach the entry point: unauthenticated, any user, admin only. This changes severity, not whether the flaw exists.
4. Decide:
   - No complete path: say so and stop. "Not vulnerable, because X at file:line" is a useful result.
   - Complete path: write a candidate finding to `.whitehat/findings/F-NNN-<slug>.md` using `${CLAUDE_PLUGIN_ROOT}/templates/finding.md`. Status is `candidate`. Fill "Why it might be wrong" honestly.
5. Variant check: once you have one real pattern, search the codebase for the same sink used the same way, and list the variants in the finding instead of opening one finding per copy.

Never mark a finding `confirmed` in this skill. Confirmation needs evidence: use `/whitehat:verify`.
