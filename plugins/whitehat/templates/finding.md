---
id: F-001
title: SQL injection in login email field
status: candidate        # candidate | confirmed | needs-validation | rejected
severity: high           # critical | high | medium | low | info (set when confirmed)
category: Database       # one of the 11 areas in references/generic-web-checks.md
cwe: CWE-89
location: routes/login.ts:34
source: req.body.email
sink: models.sequelize.query (raw SQL)
found_by: trace          # recon | trace | sast-triage | audit | pentest | manual
---

## Claim
One or two sentences: what an attacker controls, where it flows, what they gain.

## Data flow
Numbered hops from source to sink, each with file:line.

## Evidence
How it was verified: the exact test, request or command, and its actual output.
A candidate has no evidence yet. A finding is only `confirmed` with evidence here.

## Why it might be wrong
What would make this a false positive, and how that was ruled out.

## Fix
The smallest change that removes the flaw, and a regression test that fails before it.

## Severity guide
Critical: unauthenticated code execution, full data access or arbitrary account takeover. High: fully defeats a control with real consequences. Medium: limited blast radius. Low: needs unlikely conditions or gives little. Info: hardening with no affected principal. Severity never exceeds the demonstrated effect; when the code allows more than the deployment does, record both (`code_severity` and `effective_severity` in the front matter).
