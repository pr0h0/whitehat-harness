# Detailed MD Format (engineering deep-dive)

Header: title, date, auditor, scope, a Summary count table by severity, an
optional "What verification changed" table, an optional "Verified safe" list.
Body: `# CRITICAL|HIGH|MEDIUM|LOW|INFORMATIONAL` bands (empty bands omitted),
each with `## ID: N — Title` blocks:
`- **Severity:** … · **CVSS3:** score — vector` (or split `Code Severity` +
`Live/effective severity`), `- **Short Description:**`,
`- **Vulnerable Code Snippet:**` (nested file:line bullets),
`- **Description / Steps to Reproduce:**` (numbered if the field is a list),
optional `- **Verification note:**`, `- **Suggested Fix:**`. Optional SAST
appendix. Produced by `reportgen/detailed_md.py`.
