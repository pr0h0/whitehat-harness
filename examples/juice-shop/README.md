# Juice Shop audit copy

OWASP Juice Shop is a great audit target, but its source shows where the bugs are. The `vuln-code-snippet` comments mark the vulnerable lines, `data/static/codefixes/` contains the fixes, and the repo ships instruction files for AI agents (`AGENTS.md`, `.claude/`, `.cursor/` and others). If an agent "finds" bugs in the raw repo, that tells you nothing about how well it audits.

`prepare-audit-copy.sh` makes a copy without those:

```bash
git clone --depth 1 --branch v20.4.0 https://github.com/juice-shop/juice-shop.git
./prepare-audit-copy.sh juice-shop juice-shop-audit
```

It removes the marker comments, the codefix files, the challenge list (`data/static/challenges.yml`), `threat-model.json`, the test suites (they contain working exploits), `SOLUTIONS.md`, `REFERENCES.md`, `HALL_OF_FAME.md`, the RSN cache and the agent instruction files, then commits a git baseline so you can diff anything the agent changes.

Some hints stay on purpose. The code that solves challenges (`challengeUtils.solveIf(challenges.loginAdminChallenge, ...)`) names challenges right next to the vulnerable code, and removing it would break the app. A model may also simply remember Juice Shop from its training data. Read results on this copy as "best case", not as a measurement of how the agent will do on your own code.

The audit copy is for reading and auditing only. Juice Shop's maintainers do not want unsolicited AI-generated pull requests, so do not open PRs against Juice Shop from it.
