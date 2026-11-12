# SAST / Dependency Tooling (Phase 3)

Run every tool applicable to the package managers `detect.py` reported. Each
tool maps its output into candidate findings with the `category` shown below.
**If a tool is not installed or errors out, log that it was skipped and move
on — never fail the audit because a tool is missing.**

## npm — dependency vulnerabilities
```bash
npm audit --json
```
- Applies when `detect.py` reports `npm` in `package_managers`.
- Parse `.vulnerabilities` (or `.advisories` on older npm) — one candidate
  finding per distinct advisory, not per affected package instance.
- Maps to `category: "Dependencies"`. Severity: use npm's own
  `low/moderate/high/critical` mapped to the 5-band scale
  (`moderate` → `Medium`).
- `bug_type`: the advisory title (e.g. `"Prototype Pollution"`).

## Composer (PHP) — dependency vulnerabilities
```bash
composer audit --format=json
```
- Applies when `detect.py` reports `composer` in `package_managers`.
- Parse `.advisories` (keyed by package) — one candidate finding per CVE/
  advisory ID.
- Maps to `category: "Dependencies"`.

## pip (Python) — dependency vulnerabilities
```bash
pip-audit -f json
```
- Applies when `detect.py` reports `pip` in `package_managers`.
- `pip-audit` is a separate tool (not bundled with `pip`) — check
  `command -v pip-audit` first; if absent, log and skip (do not attempt to
  install it).
- Parse the `dependencies[].vulns[]` array — one candidate finding per vuln
  ID (e.g. `PYSEC-...`, `GHSA-...`).
- Maps to `category: "Dependencies"`.

## gitleaks — committed secrets
```bash
gitleaks detect --report-format json --report-path <tmpfile>
```
- Run regardless of detected package manager (applies to any repo).
- Check `command -v gitleaks` first; if absent, log and skip.
- Parse the report array — one candidate finding per leaked secret,
  deduplicated by rule + file (don't emit 50 findings for one secret rotated
  across history — summarize repeats in the description).
- Maps to `category: "Secrets & Env Vars"`. Severity is usually `High` or
  `Critical` depending on whether the secret still appears to be live
  (matches a currently-used env var name) or is clearly a rotated/dummy value.
- `locations[].file` / `.line` come straight from the report; include the
  matched rule name in `bug_type` (e.g. `"Committed AWS Access Key"`).

## semgrep — static pattern analysis
```bash
semgrep --json --config auto
```
- Check `command -v semgrep` first; if absent, log and skip.
- Use `--config auto` for a broad default ruleset, or a language-specific
  registry config if the repo is predominantly one language (faster, fewer
  false positives).
- Parse `.results[]` — one candidate finding per result. Map semgrep's own
  `metadata.cwe`/`metadata.owasp` into the finding's `cwe`/`owasp` fields when
  present.
- `category` depends on the rule matched — infer from the rule ID/message
  (an `eval`-injection rule → `Input Validation`; a hardcoded-secret rule →
  `Secrets & Env Vars`; a raw-SQL rule → `Database`). When ambiguous, default
  to `Input Validation`.
- Treat semgrep results as **candidates only** — they still go through Phase
  4 adversarial verification like every other finding; static pattern matches
  have a high false-positive rate on their own.

## Dependabot / Renovate presence
- Check for `.github/dependabot.yml` or a Renovate config (`renovate.json`,
  `.github/renovate.json`, `.renovaterc*`). Absence → one `Low` finding in
  `Dependencies`.

## Dependency reachability
For every High/Critical advisory, grep for the vulnerable API/function/
config of that package in app code (and in direct deps that wrap it). Note
"reachable via file:line" or "not reached (dev-only / unused API)" in the
finding and adjust severity accordingly — never mark safe merely because the
package isn't imported directly.

## General notes
- Run tools from the target repo root (or each sub-package root for
  monorepos) so lockfiles resolve correctly.
- Capture stderr on failure and log a one-line note (tool name + reason
  skipped) that ends up in `meta.sast_summary` alongside the tools that did
  run, so the report is honest about coverage.
- After parsing, every SAST-derived candidate finding still needs the same
  fields as a manually-found one (see `${CLAUDE_PLUGIN_ROOT}/templates/finding.md`) before
  it enters Phase 4 — fill `short_description`, `locations`, `suggested_fix`,
  etc. from the tool's own output rather than leaving them terse.
