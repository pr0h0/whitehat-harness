---
name: report
description: Turn confirmed findings in .whitehat/findings/ into a report (.whitehat/report.md) with severity, evidence, fixes and a methodology section. Use at the end of an audit or pentest.
disable-model-invocation: true
---

# Write the report

1. Read every file in `.whitehat/findings/`. Only `confirmed` findings go in the findings section. Count `candidate` and `rejected` ones for the methodology section.
2. Sort confirmed findings by severity, then by how easy they are to exploit.
3. For each finding: title, severity with one-sentence justification, CWE, affected location, impact in plain language, reproduction steps copied from the evidence (exactly as run), fix, and regression test.
4. Methodology: scope and authorization (from `.whitehat/scope.json`), dates, tools and models used, what was covered, what was not covered, and the candidate/confirmed/rejected counts.
5. Limitations: state plainly that AI-assisted review misses issues and that untested areas are not evidence of safety.
6. Do not invent anything that is not in the finding files. If a field is missing, write "not recorded".
7. Redact secrets, tokens and personal data from evidence.

Write `.whitehat/report.md` and reply with the executive summary (5 lines max).
