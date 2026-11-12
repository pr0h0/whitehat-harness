# Runtime Verification (Phase 5, optional)

Phase 5 only runs when the user has supplied a **target URL and credentials**
for the app being audited **and** that host is listed in `.whitehat/scope.json`
(create it with `/whitehat:scope`; the scope guard hook denies anything else).
If any of these is missing, skip this phase entirely — do not attempt to guess
a URL or use publicly-known endpoints.

## Authorization requirement (read first)

**Only test targets the user is explicitly authorized to test.** The user
requesting the audit must own the target, or have documented permission to
test it (e.g. a bug-bounty scope, a written pentest authorization, or it is
their own staging/production environment). If authorization is unclear, ask
before running any live request — do not assume that because credentials were
provided, testing is authorized. This applies even to "safe-looking" checks;
unauthorized access to a system, even read-only, can be illegal. When in
doubt, stay in Phase 4 (adversarial code review) and skip live testing.

## Authenticating

Authenticate as the application itself expects, using exactly the credentials
supplied:
- **Session or bearer token**: obtain a valid token through the app's normal
  auth flow (or use a supplied token directly); attach it the same way the
  app's own frontend would (typically an `Authorization: Bearer <token>`
  header).
- **Username/password or API key**: log in through the
  supplied credentials' normal flow; reuse the resulting session
  cookie/token for subsequent requests rather than re-authenticating per
  request.
- Never attempt to brute-force, guess, or escalate beyond the credentials
  provided.

## Testing confirmed findings safely

Runtime verification is for findings that already reached Phase 4 with a
`confirmed` verdict — it either raises confidence (`effective_severity` stays
at or near `code_severity`) or lowers it (`effective_severity` downgraded,
with the reason recorded).

- **SQL injection**: prefer non-destructive detection —
  error-based (a single quote causing a 500/DB error), boolean-based
  (`AND 1=1` vs `AND 1=2` producing different responses), or time-based
  (`SLEEP(5)`/`pg_sleep(5)` causing a measurable delay). Avoid `UNION`-based
  extraction of real data beyond what's needed to prove the vector (e.g. pull
  `version()`, not another tenant's rows) unless the user has explicitly asked
  for full impact demonstration.
- **MAC/signature issues (HMAC, JWT)**: send a request with a forged or
  stripped signature and confirm the endpoint rejects it (proving the check
  is enforced) or accepts it (proving the finding) — never forge a signature
  to then perform a state-changing action beyond what demonstrates the flaw.
- **IDOR/BOLA**: enumerate a small number of adjacent object IDs (not a full
  scan) as the authenticated identity, confirm cross-tenant/cross-user data is
  returned, and stop — do not exfiltrate or dump data beyond the minimum
  needed to prove access.
- **Rate limiting / DoS**: confirm a limit's absence with a bounded burst
  (e.g. 20–30 requests), never a sustained flood that could degrade the
  target for real users.

## Never exploit destructively

Do not perform actions that modify, delete, or corrupt real data; create
unauthorized charges; send unwanted communications (emails/SMS/webhooks) to
real users; or otherwise cause impact beyond what's needed to prove the
finding. If a finding can only be proven by a destructive action, describe
the proof-of-concept in `verification_note` instead of executing it, and note
that it was not runtime-executed for this reason.

## Recording results

For each finding tested:
- Update `verification_note` with what was actually done (request sent,
  response observed) and the conclusion — be specific enough that someone else
  could reproduce the check.
- Set `effective_severity` if the live result differs from `code_severity`
  (e.g. code-confirmed SQLi that a WAF neutralizes at runtime → downgrade,
  same as a Phase 4 downgrade but backed by a live observation instead of a
  static-code argument).
- If runtime testing fully confirms the finding with no mitigation observed,
  `effective_severity` can be left unset (equal to `severity`/`code_severity`)
  or explicitly set to the same value for clarity in the report.
