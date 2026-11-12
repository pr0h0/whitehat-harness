# findings.json Schema

The single source of truth for an audit. One file, two top-level keys:

```json
{
  "meta": { "...": "..." },
  "findings": [ { "...": "..." } ]
}
```

`scripts/reportgen/schema.py` validates this shape before any deliverable is
generated (`schema.load`). Both `meta` and `findings` are required top-level
keys (`meta` defaults to `{}` if omitted); `findings` must be a list.

## `findings[]` -- per-finding fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | int | yes | Sequential, assigned at synthesis (Phase 6). Must be unique -- the schema rejects duplicates. |
| `title` | string | yes | Short finding title. |
| `bug_type` | string | yes | e.g. `"IDOR"`, `"SQL Injection"`, `"Missing HMAC"`. |
| `category` | string | yes | **Must be one of the 11 canonical areas** -- see below. |
| `severity` | string (enum) | yes | **Must be one of the 5 bands** -- see below. |
| `code_severity` | string (enum)? | optional | Set alongside `effective_severity` when static and runtime-verified severity diverge. |
| `effective_severity` | string (enum)? | optional | Runtime-adjusted severity when different from `code_severity`. |
| `severity_note` | string? | optional | Short qualifier shown next to severity in the TSV, e.g. `"runtime-mitigated"`. |
| `cvss3_score` | number | recommended | Estimated CVSS v3 base score. |
| `cvss3_vector` | string | recommended | e.g. `AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N`. |
| `short_description` | string | yes | 1-2 sentence summary. |
| `locations` | array | yes | List of `{file, line, snippet}`. Multiple locations are supported (e.g. source + sink). `line` and `snippet` may be omitted per-entry. |
| `description_repro` | string or array | yes | Why it's a bug, impact, and steps to reproduce. A list renders as numbered steps; a string renders as prose. |
| `verification_note` | string? | optional | Added by the adversarial-verification (Phase 4) or runtime-verification (Phase 5) passes. |
| `suggested_fix` | string | yes | Actionable remediation, with code where useful. |
| `status` | string | optional | Defaults to `"Open"` if omitted downstream. Use `"Needs Validation"` when the decisive fact is outside the repo (proxy/WAF/IdP/cloud config, deployed env) — see below. |
| `date_reported` | string? | optional | `DD/MM/YYYY`. Falls back to `meta.date_reported` if absent. |
| `date_resolved` | string? | optional | `DD/MM/YYYY`. Blank by default. |
| `reported_by` | string? | optional | Defaults to `"Automated Security Audit (Claude Code)"`. |
| `cwe` | string? | optional | e.g. `"CWE-89"`. |
| `owasp` | string? | optional | e.g. `"A03:2021 - Injection"`. |

`id`, `title`, `bug_type`, `category`, `severity`, `short_description`,
`locations`, `description_repro`, and `suggested_fix` are enforced by
`schema.py` (`REQUIRED_FINDING_FIELDS`) -- a `findings.json` missing any of
these on any finding fails validation with a `SchemaError` naming the field
and index. The remaining fields are optional / generator-consumed with
sensible defaults; omitting them is safe but reduces report fidelity.

### `locations[]` entries

```json
{ "file": "src/routes/search.js", "line": 22, "snippet": "db.query(`SELECT * FROM items WHERE name LIKE '%${q}%'`)" }
```

- `file` -- required, path relative to repo root.
- `line` -- optional int. Omit for file-level findings.
- `snippet` -- optional string, the vulnerable line(s) or config value.

### The 11 canonical `category` values

```
Secrets & Env Vars
Auth & Authorization
Session Security
CORS
Database
Input Validation
Third-Party Integrations
Dependencies
Rate Limiting
DoS
Information Disclosure
```

Any other value fails schema validation. This list is the same one used for
`meta.area_assessments` and the exec-summary's Overall Assessment table.

### The 5 `severity` bands (ordered, highest first)

```
Critical
High
Medium
Low
Informational
```

Any other value fails schema validation. `code_severity` and
`effective_severity`, when present, must also be drawn from this list.

### Severity calibration (apply before picking a band)

Severity reflects **demonstrated** impact, never the bug-class name.

- **Critical** — unauthenticated actor gains code execution, full data-store
  access, or takeover of arbitrary accounts/shops.
- **High** — fully defeats an explicit security control with real
  consequences: auth bypass, cross-tenant read/write, stored XSS hitting other
  users, authenticated RCE, unauthenticated stop of a shared service.
- **Medium** — real boundary violation with limited blast radius, uncommon
  preconditions, or confined to a narrow resource set.
- **Low** — disclosure of non-secret internals, or an effect needing
  sustained effort for minimal gain.
- **Informational** — confirmed but minimal-impact observation, or a missing
  best practice with no affected principal/resource (hardening).

High vs Medium: does the result **fully defeat** a control for an action with
real consequences, or only weaken it? If you can't state the concrete damage,
the severity is lower than it feels.

### Needs Validation

When a candidate is source-grounded but the deciding fact is not in the repo
(reverse proxy strips headers? WAF? cookie domain in prod? IdP policy? open
ports?), do **not** guess either way. Keep the finding with
`status: "Needs Validation"`, set `severity` to the impact *if* the missing
fact goes the bad way, and state in `verification_note` the exact missing
fact and the safe check the owner can do to resolve it. Never use this as a
parking spot for speculative ideas — a candidate refuted by source is removed.

## `meta` -- fields consumed by the report generator

| Field | Type | Notes |
|---|---|---|
| `project_name` | string | Used in every deliverable's header/title. |
| `organization` | string | Shown in the exec-summary header. |
| `audit_date` | string | ISO `YYYY-MM-DD`. Also used to name the detailed-MD file (`SECURITY_AUDIT_{date with `-` to `_`}.md`); falls back to `UNDATED` if absent. |
| `date_reported` | string | `DD/MM/YYYY`. Default for any finding's own `date_reported`. |
| `auditor` | string | Shown in the detailed-MD header. |
| `scope[]` | array of strings | Repos/stack/entry points audited; rendered as a bullet list. |
| `summary_paragraph` | string | 2-3 sentence overall-posture narrative for the exec summary. |
| `area_assessments[]` | array of `{area, result, summary}` | One entry per one of the 11 areas. `result` is one of `Passed \| Good \| Fix`. `summary` is one sentence. Feeds the exec-summary Overall Assessment table. |
| `verification_changes[]` | array of `{change, findings, reason}` | What the adversarial/runtime verification pass altered (e.g. downgrades, removals). Feeds the detailed-MD "What verification changed" table. Omit (or empty) if verification changed nothing. |
| `verified_safe[]` | array of strings | Things explicitly checked and confirmed NOT vulnerable (checked, not assumed). Feeds the detailed-MD "Verified safe" list. |
| `sast_summary` | string | Free-text summary of the SAST/dependency pass (Phase 3), e.g. `"npm audit -> 12 advisories (2 high, reachable: 1); semgrep -> 9 results, 3 kept after verification; gitleaks -> 1 committed .env file."` Feeds the detailed-MD appendix. |
| `remediation_steps[]` | array of `{title, estimate?, summary?, instructions[]}` | Grouped, priority-ordered fix guide. `estimate` is a free-text effort estimate (e.g. `"2h"`). Feeds the exec-summary Remediation Guide appendix. |

`meta` is optional overall (defaults to `{}`), but the report generator
degrades gracefully rather than failing when narrative fields are missing --
see `skills/report/SKILL.md` for which fields to
backfill before generating deliverables.

## Minimal valid example

```json
{
  "meta": {
    "project_name": "SampleApp",
    "audit_date": "2026-07-24"
  },
  "findings": [
    {
      "id": 1,
      "title": "Missing HMAC verification on webhook endpoint",
      "bug_type": "Missing HMAC",
      "category": "Third-Party Integrations",
      "severity": "High",
      "short_description": "The /webhooks/payments route trusts the payload without verifying the provider's signature header.",
      "locations": [{"file": "src/routes/webhooks.js", "line": 12}],
      "description_repro": "Any client can POST a forged order payload; the handler processes it as genuine.",
      "suggested_fix": "Verify the HMAC header against the raw request body using the shared webhook secret (constant-time compare) before processing."
    }
  ]
}
```
