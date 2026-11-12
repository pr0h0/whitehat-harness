# Generic Web App Checklist — the 11 Areas

Always applied. Each area below is a `category` value in a finding file and in
`findings.json` (must match exactly — see `${CLAUDE_PLUGIN_ROOT}/templates/finding.md`), with concrete
things to look for.

## 1. Secrets & Env Vars
- Hardcoded secrets, API keys, or credentials in source (including test
  fixtures, seed scripts, and commit history).
- Committed `.env`/`.env.*` files, or example env files that contain real
  (not placeholder) values.
- Fallback/default values for secrets (`env('SECRET', 'changeme')`,
  `process.env.KEY || 'test-key'`) that silently defang a security check when
  the env var is unset.
- Missing startup validation for required secrets (app boots successfully
  with no secret configured, rather than failing fast).
- Secrets echoed into logs, error messages, or verbose debug output.

## 2. Auth & Authorization
- Auth-bypass flags/feature switches (`SKIP_AUTH`, `DEBUG_NO_AUTH`) without a
  hard production guard.
- Privilege-escalation paths: role/permission checks that can be influenced by
  client-supplied input (body/query params setting `role` or `is_admin`).
- Authorization checks keyed on unstable identifiers (display name, email
  string match) instead of stable IDs.
- Mutation endpoints (create/update/delete) missing an authorization check
  present on the corresponding read endpoint.
- Route-level protection coverage: enumerate routes and confirm every
  sensitive one sits behind auth middleware — an unprotected route is a
  finding even with no other bug.

## 3. Session Security
- Cookie flags: `Secure`, `HttpOnly`, `SameSite` (Lax/Strict, not None without
  a compensating CSRF control).
- `trust proxy` / `X-Forwarded-*` handling — trusting these headers without a
  real reverse proxy in front can spoof IP-based logic (rate limiting, geo
  checks).
- Session-store config: `resave`/`saveUninitialized` (Express) or equivalent
  defaults that create session-fixation or session-bloat issues.
- Session-secret strength (long, random, not a hardcoded default).
- Session fixation: session ID is regenerated on login/privilege change, not
  reused from the pre-auth session.
- Session expiry: idle timeout and absolute timeout both exist and are
  enforced server-side, not just client-side.

## 4. CORS
- Wildcard `Access-Control-Allow-Origin: *` combined with
  `Access-Control-Allow-Credentials: true` (invalid per spec but sometimes
  shipped anyway, and browsers may still leak in edge cases).
- Origin reflection: server echoes the request's `Origin` header back
  unchecked instead of validating against an allowlist.
- Preflight (`OPTIONS`) handling: mutating routes actually require and check
  preflight, not bypassable via a `text/plain`-content-type trick.
- Overly broad allowlists (e.g. all `*.example.com` subdomains when only one
  is legitimate, and subdomain takeover is plausible).

## 5. Database
- SQL injection via raw queries or string concatenation (`whereRaw`,
  `$db->query("... $var ...")`, template-literal SQL).
- ORM/query-builder misuse that defeats parameterization (building a raw
  fragment from user input and passing it through `raw()`/`DB::raw()`).
- RPC/stored-procedure calls that pass user input unsanitized.
- Missing or misconfigured Row-Level Security (RLS) policies on multi-tenant
  databases (Postgres RLS, Supabase policies).
- NoSQL injection via unsanitized operator injection (`{"$ne": null}` style
  payloads in MongoDB queries built from request bodies).

## 6. Input Validation
- XSS sinks: `dangerouslySetInnerHTML`, `innerHTML`, `v-html`, template
  `|safe`/`|raw` filters, or direct DOM writes of user-controlled data.
- `eval`, `Function(...)`, `vm.runInNewContext`, or PHP `eval`/`create_function`
  fed by any request-derived value.
- Missing length limits on user-controlled fields (uncapped strings/arrays
  feeding into expensive operations — also a DoS concern, see §10).
- Missing type checks / missing allowlists on enum-like fields (a "status"
  field accepting arbitrary strings instead of a fixed set).
- Unescaped user input interpolated into templates, shell commands
  (`exec`/`system`/backticks), file paths, or URLs.

## 7. Third-Party Integrations
- Webhook signature verification (Stripe, Slack, GitHub, etc.): HMAC over
  the raw body, constant-time compare, verified before any processing, no
  fallback when the secret is unset.
- Secret fallbacks that defang verification (see §1).
- Replay protection: timestamp/nonce checks where the provider supports them
  (e.g. Stripe's `Stripe-Signature` timestamp tolerance).
- Error handling on verification failure: fails closed (rejects), not open.

## 8. Dependencies
- Run the SAST/dependency tools per `references/sast-tools.md` and list every
  advisory found, mapped to `category: "Dependencies"`.
- Note whether advisories are reachable from actual app code paths vs.
  purely transitive/dev-only, to help prioritize severity.

## 9. Rate Limiting
- Rate-limiting middleware presence and per-route configuration, especially
  on: login, password reset, OTP/2FA verification, signup, and any endpoint
  that triggers an expensive operation (email send, report generation,
  external API call).
- Limits keyed on something the attacker can't trivially reset (account/user,
  not just IP, where credential-stuffing is the threat).

## 10. DoS
- Unbounded connections: SSE/WebSocket endpoints with no per-client or global
  connection cap.
- Unbounded request body size (no `Content-Length` cap, no streaming size
  guard) on upload or JSON-body endpoints.
- Expensive operations (regex, recursive parsing, large joins, PDF/image
  generation) reachable without a concurrency guard or timeout.
- Missing timeouts on outbound calls to third parties, allowing a slow
  upstream to exhaust the app's own worker pool.

## 11. Information Disclosure
- Verbose error messages / stack traces returned to clients in production.
- Debug endpoints or admin tooling (Laravel Telescope, Django debug toolbar,
  GraphQL introspection, `/actuator`, `/.env`) reachable outside a dev
  environment.
- Internal schema/table/column names or file paths leaked in error responses.
- Overly detailed `X-Powered-By`/server headers or version banners that aid
  targeting (informational severity, but worth noting).

---

# Attack classes beyond the checklist

The 11 areas above are the *reporting* buckets. Hunting needs more: the
classes below catch what checklists miss (adapted from Cloudflare's
security-audit skill). Each lists the canonical `category` to file under.

## Access control depth — `Auth & Authorization`
Don't stop at "a check exists"; verify it is the *right* check for the
*right* resource via the *right* mechanism:
- Another path to the same state change with a weaker check (legacy/v1
  route, batch endpoint, GraphQL resolver, admin "impersonate", job retry).
- A body field overriding what the permission system restricts (mass
  assignment: `role`, `owner_id`, `tenant_id`, `is_admin`, `price`).
- Authenticated but not authorized (any logged-in user can hit it).
- Bulk/batch/export/import enforce per-item authorization, not per-request.

## Business logic — `Auth & Authorization` (or the area of the asset)
Scanners can't find these; they are high-yield. For each major workflow:
- **State machine:** skip steps, go backwards, replay a completed flow;
  partial failure (step 2 of 3 fails) leaves step 1 committed.
- **Races:** check-then-act without a transaction/lock/unique constraint →
  double spend, double redeem, double approve, lost updates.
- **Numbers:** negative/zero/huge quantities, float precision, string↔number
  coercion, currency mismatch.
- **Implicit trust:** data from DB/config/another component assumed
  validated because "we validated it on the way in" — some other path wrote it.
- **Time:** expiry at exact boundaries, timezone mismatch, clock skew.
- **Defaults/fallbacks:** posture when config is missing, a feature flag is
  off, a dependency is down, or mid-migration — fail open?

## Feature abuse & data leakage — `Information Disclosure`
- **Export/backup** includes data above the caller's access, other users'
  data, deleted/draft content.
- **Import/restore** overwrites others' data or bypasses validation.
- **Search/filter/sort as oracle:** filtering or sorting by hidden fields
  leaks their values; search reveals existence of inaccessible records.
- **Enumeration:** different errors/status/timing for "doesn't exist" vs "no
  access"; user enumeration via reset/invite/signup (only a finding if
  account existence is actually sensitive).
- **Preview/draft tokens** unlock more than one item; cache headers let a CDN
  serve private responses publicly.
- **User-set URLs** (webhook/notification/callback/avatar/import-from-URL) →
  SSRF; check internal-IP blocking survives redirects and DNS rebinding.
- **Logs, analytics, error trackers, search indexes, caches** as alternate
  readers holding data without the original ACL.

## Data lifecycle — `Database` / `Information Disclosure`
- Soft-deleted / tombstoned records still reachable by direct ID, search,
  export, or relations.
- Revocation (logout, role removal, uninstall, password change) doesn't
  invalidate cached/derived copies, tokens, or queued jobs.
- Deletion/redaction misses copies (S3, search index, analytics, backups,
  third-party processors) — matters for GDPR/redact webhooks.
- Restore/undelete re-applies stale ownership or skips current validation.

## Second-order & chained — `Input Validation`
- Data safe when stored becomes dangerous elsewhere: a name becomes a file
  path, a slug a URL, escaped text later rendered raw, a stored string a
  regex/template/JSON path.
- Component A validates, component B assumes a stronger guarantee
  (truncation, normalization, tenant scope). Compare exactly.
- Low-severity outputs feeding later trust decisions (open redirect → OAuth
  token theft; self-XSS + CSRF → stored XSS). Confirm each link.

## HTTP & identity protocol — `Auth & Authorization` / `Session Security`
- **JWT:** signature actually verified; algorithm pinned server-side (no
  `none`, no RS→HS confusion); `exp`/`nbf`/`aud`/`iss` checked; `kid`/`jku`/
  `x5u` treated as untrusted; no `decode()`-without-verify path used for
  authz. A valid token for another service is invalid here.
- **OAuth/OIDC:** session-bound `state`; PKCE where applicable; exact
  `redirect_uri` match (if you're the AS); ID token issuer/audience/nonce;
  account-linking callbacks bound to the initiating account.
- **CSRF:** inventory every cookie-authenticated mutation (form, JSON,
  multipart, method-override, legacy). Name the ambient credential and the
  accepted cross-site request shape. Bearer-token-only routes don't qualify.
- **Session fixation/invalidation:** rotate on login, MFA completion,
  privilege change; invalidate on logout, password change, account disable —
  including refresh tokens and websocket sessions.
- **Password reset / recovery / MFA:** CSPRNG token, bound to user+action,
  short expiry, single-use, prior tokens invalidated, reset link host not
  built from the `Host` header; MFA enrollment/disable requires fresh auth;
  every login path (API, SSO, recovery) enforces MFA.
- **Host / X-Forwarded-* trust:** used for absolute URLs, reset links, tenant
  routing, cache keys, or client IP — confirm the proxy strips client copies.
- **Cache deception/poisoning:** private dynamic responses cacheable (missing
  `Cache-Control: private`/`no-store`), or unkeyed headers changing output.
- **API keys:** scoped to tenant/resource server-side; publishable vs secret
  key confusion; revocation honored by caches.

## Client-side / browser — `Input Validation` / `CORS`
- **DOM XSS:** `location`/`hash`/`postMessage`/storage → `innerHTML`,
  `document.write`, `eval`, `setTimeout(string)`, jQuery `$(html)`,
  `href="javascript:"`.
- **postMessage:** handlers that don't check `event.origin` (or use
  `indexOf`/unanchored regex); senders using `targetOrigin: "*"` with
  sensitive data.
- **Prototype pollution:** deep-merge/`_.set`/query parsers on user JSON
  reaching a gadget (`isAdmin`, template options, child_process options).
- **Clickjacking:** sensitive actions frameable (no `frame-ancestors` /
  `X-Frame-Options`).
- **WebSockets:** handshake doesn't validate `Origin` with cookie auth
  (cross-site WebSocket hijacking); per-message authz.
- **Storage:** tokens/PII in `localStorage` surviving logout; service worker
  caching authenticated responses across users.
- `target="_blank"` without `rel=noopener` on user-controlled links
  (reverse tabnabbing — usually Low).

## Resource exhaustion — `DoS`
- **Superlinear work:** ReDoS (nested quantifiers on user input), GraphQL
  depth/alias/batch amplification, N+1 or unbounded `LIMIT`/pagination, XML
  entity expansion.
- **Decompression/representation bombs:** zip/gzip/image pixel-count bombs,
  huge JSON arrays.
- **Accumulation:** unbounded in-memory maps/caches keyed by user input,
  leaked file handles/temp files, work that continues after the client
  disconnects.
- **Pre-auth imbalance:** expensive work (bcrypt, PDF render, outbound
  calls, email send) before authentication or rate limiting.
- **Failure modes:** retry storms, poison messages blocking a queue, a
  reachable `throw` that kills a worker process.

## Supply chain & CI — `Dependencies`
- GitHub Actions: `pull_request_target` / `workflow_run` checking out and
  running PR code with secrets; `${{ github.event.* }}` interpolated into
  `run:` (script injection); third-party actions not pinned to a SHA;
  over-broad `permissions:`.
- Dependency confusion: internal package names resolvable from the public
  registry; missing/uncommitted lockfile; `postinstall` scripts in deps.
- Dockerfile/build context copying `.env`, `.git`, or keys into images.

## AI / LLM features (only if present) — `Input Validation`
- Indirect prompt injection: retrieved/ingested content (product
  descriptions, emails, reviews, web pages) reaching a model that can call
  tools or render output.
- Tool calls executed with the app's authority rather than the requesting
  user's (confused deputy) — cross-tenant reads/writes via tool arguments.
- Model output rendered as HTML/markdown (XSS, image-URL exfiltration) or
  passed to SQL/shell/URL sinks.
- Cross-tenant context bleed via shared memory, caches, or vector stores
  without tenant filters; system prompt containing secrets.

## Wildcard pass
Not a category — a mindset for one agent:
- What's the strangest code? Half-finished, experimental, `legacy`, `temp`,
  `hack` code gets the least review.
- What API calls are possible but the frontend never makes? The UI
  constrains users; the API doesn't.
- Hidden/undocumented routes, params, headers (read route registration and
  middleware, not docs).
- Feature combinations not designed together (impersonation + API keys,
  import + webhooks, preview + caching).
- Git history: reverted security fixes, commented-out auth checks, secrets
  committed then removed (`git log -p -S`).
- What do the tests *not* cover? Comments claiming "safe because…" — verify.

## "Obvious things" sweep
Literal, exhaustive, every item reported as checked: hardcoded
passwords/keys/`-----BEGIN`; `TODO/FIXME/HACK` mentioning auth/validation;
debug mode toggleable via env/query/header; seed/test credentials that work in
prod; unprotected `/debug` `/admin` `/test` `/metrics` `/env` `/actuator`
`/graphql` (introspection) `/telescope` `/horizon`; committed `.env`,
`*.pem`, `*.key`, `credentials.json`; `.gitignore` gaps; `eval`/`exec`/
`Function`/dynamic `import()`/`child_process` with dynamic input; wildcard
CORS + credentials; cookies missing flags; redirect params (`redirect`,
`return`, `next`, `url`, `goto`, `continue`, `return_to`); plain-HTTP
endpoints; stack traces / SQL errors in prod responses. **A flag is not a
finding** — trace impact before reporting (does the cookie hold anything
sensitive? is the field ever populated?).
