---
id: F-001
title: SQL injection in login email field
status: candidate        # candidate | confirmed | rejected
severity: high           # critical | high | medium | low | info (set when confirmed)
cwe: CWE-89
location: routes/login.ts:34
source: req.body.email
sink: models.sequelize.query (raw SQL)
found_by: trace          # recon | trace | sast-triage | pentest | manual
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
