# TSV Format (spreadsheet import)

Tab-separated, header row first, exactly 11 columns, one row per finding:

`ID · Bug Type · Short Description · Suggested fix · Screenshot · Status ·
Severity · Date Reported · Date Resolved · Reported By ·
Description/Steps to reproduce`

Fixed literals: Screenshot = `Add screenshot here`; Status = `Open` (unless the
finding overrides); Reported By = `Automated Security Audit (Claude Code)`;
dates `DD/MM/YYYY`; Date Resolved blank. Severity shows `severity` plus an
optional `(severity_note)` qualifier. The Description cell is flattened to one
line, prefixed `Location/Evidence:` with every `file:line — snippet`, followed
by the repro text and any verification note. Produced by `reportgen/tsv.py`.
