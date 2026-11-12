---
name: audit
description: Full whitebox security audit of a codebase in one run - scope note, parallel region and domain auditors, a coverage critic, scanners, skeptic verification of every candidate, then the report. Use when the user asks for a complete audit rather than one trace.
argument-hint: "[path] [in-scope base URL for runtime checks]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash(python3 *), Bash(command -v *)
---

# Full audit

Target: $ARGUMENTS (first word: path, default `.`; second, optional: a base URL for runtime checks).

This is the orchestrated version of recon -> sast-triage -> trace -> verify -> report. It writes the same files, so you can stop after any phase and continue with the single skills. Announce each phase as you start it.

**Run every phase.** On a small codebase you may use one region auditor for the whole tree and fold the domain checks into one auditor, but the scanner pass, the skeptic verification and the report always run. If a phase cannot run (a tool is missing, a permission is denied), record that in `.whitehat/coverage.md` and say so in the final reply; never skip a phase silently.

**Statuses.** `confirmed` needs evidence produced in this run: a failing test or a request to a host in `.whitehat/scope.json`. A flaw that the code clearly supports but nobody executed is `needs-validation`, with "no runtime evidence" as the missing fact. Code review alone never makes a finding `confirmed`.

## Core rule
Every finding names the **lower-trust principal** (anonymous user, other tenant, lower-privilege role), the **input or action** they control, the **control** that should stop it, the **boundary crossed**, and the **concrete result**. No principal or no result: not a finding (at most Info hardening).

## Phase 1: scope
1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect.py <path>` for the package managers.
2. If `.whitehat/recon.md` exists, use it; otherwise run the recon workflow (`/whitehat:recon`) first.
3. If `.whitehat/findings/` already has files, re-check their status against the current code instead of rediscovering them, and prioritise areas they marked uncovered.
4. Write a **scope note** (under ~600 words) that every auditor receives: stack, entry points, principals and what each may do, tenant key, trust boundaries and the strongest control on each, protected assets. Save it as `.whitehat/scope-note.md`.

## Phase 2: parallel fan-out
Dispatch `auditor` subagents (agent type `whitehat:auditor`) **in parallel** (several Agent calls in one message), each with the scope note:
- **Region auditors:** one per module or file group, sized to fit comfortably in context, following `${CLAUDE_PLUGIN_ROOT}/references/taint-analysis.md`. Log any region not covered; never drop one silently.
- **Domain auditors:** one per concern, with the matching section of `${CLAUDE_PLUGIN_ROOT}/references/generic-web-checks.md` pasted into the prompt: secrets; dependencies and CI; CORS, headers and config; access control and business logic (state machines, races, numbers); feature abuse and data lifecycle; HTTP and identity protocol (JWT, OAuth, CSRF, sessions, reset/MFA) plus client-side; DoS; information disclosure; tenant isolation (multi-tenant apps only); AI/LLM (only with model integrations); a **wildcard** pass for odd or legacy code; an **obvious-things** sweep of the checklist.
- **Variants:** when an auditor reports a High or Critical root cause, dispatch a follow-up auditor to look for the same mistake elsewhere.

Then dispatch one more `auditor` as **coverage critic** with the scope note, the assignments and the candidate titles. It returns gaps only. Run one follow-up wave for them. Anything still uncovered is written to `.whitehat/coverage.md` as "Not covered: ...".

## Phase 3: scanners
Follow `${CLAUDE_PLUGIN_ROOT}/references/sast-tools.md` (or `/whitehat:sast-triage`) for the detected package managers. Check each tool with `command -v` first. A missing tool is logged in `.whitehat/coverage.md` and skipped, never fatal, never treated as a clean result.

## Phase 4: candidates and verification
1. Deduplicate by root cause: one root cause reachable from several routes is one finding with several locations.
2. Write each remaining candidate to `.whitehat/findings/F-NNN-<slug>.md` using `${CLAUDE_PLUGIN_ROOT}/templates/finding.md`, status `candidate`, `found_by: audit`, with `category` from the 11 areas.
3. For each candidate, dispatch the `skeptic` agent (`whitehat:skeptic`) (in parallel where possible) with only the finding file, the scope note and the scope file, not the auditor's reasoning. Apply its verdict to the file.

## Phase 5: runtime checks (optional)
Only when a base URL was given **and** its host is in `.whitehat/scope.json`. Follow `${CLAUDE_PLUGIN_ROOT}/references/runtime-verification.md` for `confirmed` and `needs-validation` findings: one minimal, harmless request per finding, evidence recorded in the finding file.

## Phase 6: report
Read `${CLAUDE_PLUGIN_ROOT}/skills/report/SKILL.md` and follow both of its sections: the narrative `.whitehat/report.md`, then `.whitehat/findings.json` and the generated deliverables in `.whitehat/report/`. Report the written paths, the counts per status, and the "Not covered" list.

## Anti-patterns
1. Checklist deviations (missing header, cookie flag) reported as vulnerabilities without an affected principal and result.
2. Guessing proxy, WAF, identity-provider or cloud behaviour that is not in the repo: use `needs-validation`.
3. Self-impact presented as a boundary crossing (an admin breaking their own settings page).
4. Severity stronger than the demonstrated effect.
5. Prose-only auditor output that cannot be deduplicated or verified.
6. Writing the report before verification.
