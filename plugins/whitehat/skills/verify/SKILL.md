---
name: verify
description: Try to disprove a candidate finding, then confirm it only with reproducible evidence (a failing test or an in-scope request). Use on any finding in .whitehat/findings/ with status candidate.
argument-hint: "<finding id or file, e.g. F-003>"
context: fork
agent: skeptic
---

# Verify a finding

Finding: $ARGUMENTS (look it up in `.whitehat/findings/`; if empty, take the oldest `candidate`).

Your job is to prove the finding wrong. Confirm it only if you fail.

1. Re-read every `file:line` in the data flow yourself. If a hop does not exist or does not behave as written, mark the finding `rejected` and say why.
2. Look for the defense the author missed: middleware, validation schemas, ORM escaping, framework encoding, auth on the route, config that turns the feature off.
3. Produce evidence with the least invasive method that proves the point:
   - Preferred: a test in the project's own test framework that fails because of the flaw. Run it and keep the output.
   - Against a running target: only hosts listed in `.whitehat/scope.json`, one request at a time, read-only where possible. Record the exact command and response.
   - Never test against anything else, never cause lasting damage, never exfiltrate real data. Use a harmless marker to show impact.
4. Update the finding file:
   - `confirmed`: evidence section holds the command or test and its real output, severity is set, and a fix plus regression test are proposed.
   - `rejected`: the reason, with `file:line`.
   - leave `candidate` if you could not decide, and say what is missing.
5. Reply with the new status and one line of justification.
