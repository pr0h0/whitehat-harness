# Taint Analysis Methodology

Region agents (Phase 2, region mode) must trace data flow from **sources**
(attacker-influenced input) to **sinks** (dangerous operations), not just
pattern-match for risky-looking function calls. A sink call is only a finding
if a source can actually reach it — cite the path, not just the sink.

## Sources — enumerate all attacker-influenced input
- HTTP request data: query params, path params, request body (JSON/form/
  multipart), headers (including `X-Forwarded-*`, `Referer`, `User-Agent` when
  used in logic), cookies.
- Webhook payloads (Stripe, Slack, GitHub, etc.) — untrusted until
  signature-verified (see `generic-web-checks.md` §7).
- Database reads whose values originated from user input at write time (e.g.
  a stored profile field later rendered or interpolated elsewhere — "second
  order" injection).
- Responses from third-party APIs the app calls, when those APIs return
  data that ultimately reflects another user's input (e.g. a marketplace
  product feed, an OAuth-provider profile field).
- File uploads: filename, content-type, and file contents.
- Platform and plugin contexts: tenant/account selectors in query params,
  `return_to`/`next` URLs, signed-proxy parameters (until the signature is
  verified), settings editable by lower-privilege roles, shared key-value or
  custom-field stores writable by other integrations, unverified webhook bodies.
- `postMessage` events, `location.hash`/`search`, browser storage (for
  client-side code).
- Environment/config values only if they are themselves derived from user
  input indirectly (rare — usually out of scope as a source).

## Sinks — enumerate all dangerous operations
- **SQL/ORM raw queries**: `whereRaw`, `selectRaw`, `DB::raw`, string-built
  SQL, raw drivers (`mysqli_query`, `psycopg2.execute` with `%`-formatting).
- **DOM/HTML render**: `innerHTML`, `dangerouslySetInnerHTML`, `v-html`,
  unescaped template output (`{!! !!}` in Blade, `|safe` in Jinja/Twig),
  server-rendered string concatenation into HTML.
- **`eval`/command exec**: `eval`, `Function(...)`, `vm.runInNewContext`,
  PHP `eval`/`assert`/`create_function`, `exec`/`system`/`popen`/backticks,
  `child_process.exec` (vs. `execFile`/`spawn` with an argument array).
- **File paths**: any sink that opens/reads/writes/deletes a file using a
  user-influenced path segment (path traversal, arbitrary file read/write).
- **External URLs (SSRF)**: any outbound HTTP call, webhook-retry, image
  proxy, or "fetch this URL" feature where the URL or host is user-supplied.
- **Redirects / headers**: `redirect()`, `Location`, `Set-Cookie`, CSP
  built from input (open redirect, header injection).
- **Tenant/context selectors**: any value that picks *which* tenant/
  account the operation runs as — a client built from a request-supplied
  tenant id, session lookup by tenant, `WHERE tenant_id = ?` with a
  request-derived tenant. Treat as a
  sink equal to SQL.
- **Template output**: server-side templates rendering unescaped values
  (`{{{ }}}`, `| safe`, `|raw`, `dangerouslySetInnerHTML`), injected script
  `src` values.
- **Logs and client payloads** (for credentials): logger calls, loader /
  API responses, `window` globals.
- **De/serialization**: `unserialize` (PHP), `pickle.loads` (Python),
  `Marshal.load` (Ruby), unsafe `yaml.load` (vs. `safe_load`), Java
  `ObjectInputStream` — on data that isn't strictly first-party-signed.

## Tracing reachability
1. Start at the sink; walk backwards through the call graph/data flow to find
   where each argument originates.
2. Confirm the source is genuinely reachable from an unauthenticated or
   attacker-controlled context — dead code, admin-only tooling behind a
   separate auth layer, or CLI-only scripts are lower priority (note them as
   Informational/Low rather than dropping silently).
3. Walk forward from the source through every transformation (validation,
   escaping, casting, allowlist filtering) between source and sink. A single
   validated hop does not clear the whole path — check each hop.
4. If a sanitizer/validator is present, read what it actually does (e.g. a
   `min:2|max:255` string rule does nothing against SQL metacharacters) rather
   than assuming a rule named "validation" is sufficient.

5. Check every **parallel path** to the same sink or state change (v1/v2
   routes, batch/bulk endpoints, GraphQL resolvers, jobs, retries, error
   handlers) — the weakest one defines the real control.
6. Check **second-order** flows: input stored safely here, used dangerously
   elsewhere by different code (stored → rendered raw, stored → file path).

## Framework scopes/traits that may neutralize a sink
Before flagging a data-layer finding as exploitable, check for a framework
mechanism that scopes the sink even though the raw code looks vulnerable:
- **Laravel global scopes / traits** (e.g. a `Tenant`/`BelongsToTenant` trait
  applying a `where tenant_id = ?` on every query for the model) — a `whereRaw`
  on a model using such a trait may be tenant-isolated even though the SQL
  fragment itself looks unscoped. Read the model definition, not just the
  repository method.
- **ORM default scopes** in other frameworks (Django managers, Rails default
  scopes, Eloquent global scopes).
- **Middleware-layer guards**: WAF rules, framework-level CSRF middleware,
  a validation-request class applied at the route level rather than in the
  method body.
- **Database-layer RLS policies** (Postgres/Supabase) that would reject a
  cross-tenant row even if the application query itself is unscoped.

When a neutralizing mechanism is found, either don't report the finding, or
report it as Low/Informational "defense-in-depth" with the mechanism named —
this is exactly the kind of judgment call the `skeptic` verifier (Phase 4) will
re-check adversarially, so cite the specific trait/scope/policy by name and
file so it can be verified.
