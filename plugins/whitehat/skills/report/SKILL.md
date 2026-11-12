---
name: report
description: Turn findings in .whitehat/findings/ into a report (.whitehat/report.md) plus standard deliverables generated from findings.json (detailed technical report, issue-tracker TSV, executive summary). Use at the end of an audit or pentest.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash(python3 *)
---

# Write the report

## 1. The narrative report
1. Read every file in `.whitehat/findings/`. `confirmed` findings go in the findings section. `needs-validation` findings go in their own section, each with the missing fact and the owner-side check that would settle it. Count `candidate` and `rejected` ones for the methodology section.
2. Sort by severity, then by how easy the finding is to exploit.
3. For each finding: title, severity with one-sentence justification, CWE, affected location, impact in plain language, reproduction steps copied from the evidence (exactly as run), fix, and regression test.
4. Methodology: scope and authorization (from `.whitehat/scope.json`, if present), dates, tools and models used, what was covered, what was not covered (`.whitehat/coverage.md`, if present), and the counts per status.
5. Limitations: state plainly that AI-assisted review misses issues and that untested areas are not evidence of safety.
6. Do not invent anything that is not in the finding files. If a field is missing, write "not recorded".
7. Redact secrets, tokens and personal data from evidence.

Write `.whitehat/report.md`.

## 2. The generated deliverables
1. Build `.whitehat/findings.json` from the `confirmed` and `needs-validation` findings, following `references/findings-json-schema.md` in this skill's folder. Map front matter to fields: `title`, `bug_type` (the weakness, e.g. "SQL Injection"), `category` (must be one of the 11 areas), `severity` in Title Case (`Critical|High|Medium|Low|Informational`; `info` becomes `Informational`), `locations` from the data-flow hops, `description_repro` from the evidence, `suggested_fix` from the fix. `needs-validation` findings get `"status": "Needs Validation"` and the missing fact in `verification_note`. Fill `meta` (project name, dates, scope, summary paragraph, one assessment per area, remediation steps) from the narrative report, never from guesses.
2. Run the generator:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/reportgen/cli.py .whitehat/findings.json --out .whitehat/report --slug <project-slug>
   ```
3. If it raises a `SchemaError`, fix the offending record in `findings.json` and run it again. Never edit the generated files by hand; regenerate them.

Reply with the written paths and the executive summary (5 lines max).
