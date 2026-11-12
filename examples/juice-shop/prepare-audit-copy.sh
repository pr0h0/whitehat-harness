#!/usr/bin/env bash
# Make an audit copy of OWASP Juice Shop without the planted answers:
# vuln-code-snippet markers, codefix files, solution lists and AI-agent instruction files.
# Usage: prepare-audit-copy.sh <juice-shop clone> <output dir>
# ponytail: challenge-solving code (e.g. challengeUtils.solveIf(challenges.loginAdminChallenge ...))
# stays, because removing it breaks the app; it still hints at bug locations by name.
set -euo pipefail
src=${1:?juice-shop clone}; out=${2:?output dir}
[[ -e "$out" ]] && { echo "$out exists; remove it first" >&2; exit 1; }
rsync -a --exclude .git --exclude node_modules "$src"/ "$out"/
cd "$out"
rm -rf data/static/codefixes data/static/challenges.yml threat-model.json test HALL_OF_FAME.md REFERENCES.md rsn SOLUTIONS.md AGENTS.md .claude .cursor .continue .junie .codeium .ai .github/copilot-instructions.md
# strip marker comments in every style the repo uses (//, #, <!-- -->), keep the code on the line
grep -rlI 'vuln-code-snippet' . | while read -r f; do
  sed -E -i.bak -e 's@[[:space:]]*//[[:space:]]*vuln-code-snippet.*$@@' \
    -e 's@[[:space:]]*#[[:space:]]*vuln-code-snippet.*$@@' \
    -e 's@[[:space:]]*<!--[[:space:]]*vuln-code-snippet.*-->@@' "$f" && rm -f "$f.bak"
done
git init -q && git add -A && git -c user.name=audit -c user.email=audit@localhost commit -qm "audit baseline"
echo "audit copy ready in $out"
echo "left on purpose: code that parses markers (lib/codingChallenges.ts, server.ts) and challenge-solving calls"
