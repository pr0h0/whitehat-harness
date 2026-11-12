from reportgen import constants

def _by_band(findings):
    bands = {s: [] for s in constants.SEVERITY_ORDER}
    for fnd in findings:
        bands[fnd["severity"]].append(fnd)
    for s in bands:
        bands[s].sort(key=lambda f: f["id"])
    return bands

def _header(data):
    meta = data.get("meta", {})
    findings = data["findings"]
    out = []
    name = meta.get("project_name", "Application")
    out.append(f"# Security Audit — {name} — SEVERITY-SORTED\n")
    if meta.get("audit_date"):
        out.append(f"**Date:** {meta['audit_date']}")
    if meta.get("auditor"):
        out.append(f"**Auditor:** {meta['auditor']}")
    if meta.get("scope"):
        out.append("**Scope:**")
        for s in meta["scope"]:
            out.append(f"- {s}")
    out.append("\n---\n")
    # Summary table
    out.append("## Summary\n")
    out.append("| Severity | Count | Finding IDs |")
    out.append("|----------|:-----:|-------------|")
    bands = _by_band(findings)
    for s in constants.SEVERITY_ORDER:
        ids = ", ".join(str(f["id"]) for f in bands[s])
        out.append(f"| {s} | {len(bands[s])} | {ids} |")
    out.append(f"| **Total** | **{len(findings)}** | |")
    # What verification changed
    if meta.get("verification_changes"):
        out.append("\n## What verification changed\n")
        out.append("| Change | Finding(s) | Reason |")
        out.append("|---|---|---|")
        for c in meta["verification_changes"]:
            out.append(f"| {c.get('change','')} | {c.get('findings','')} | {c.get('reason','')} |")
    # Verified safe
    if meta.get("verified_safe"):
        out.append("\n## Verified safe (checked, not assumed)\n")
        for v in meta["verified_safe"]:
            out.append(f"- {v}")
    out.append("\n---")
    return "\n".join(out)

def _snippet_lines(fnd):
    locs = fnd.get("locations", [])
    if len(locs) == 1 and not locs[0].get("snippet"):
        loc = locs[0]
        ref = f"{loc['file']}:{loc.get('line')}" if loc.get("line") is not None else loc["file"]
        return f"- **Vulnerable Code Snippet:** `{ref}`"
    lines = ["- **Vulnerable Code Snippet:**"]
    for loc in locs:
        ref = f"{loc['file']}:{loc.get('line')}" if loc.get("line") is not None else loc["file"]
        snip = loc.get("snippet")
        lines.append(f"  - `{ref}`" + (f" — {snip}" if snip else ""))
    return "\n".join(lines)

def _repro(fnd):
    val = fnd["description_repro"]
    if isinstance(val, list):
        body = "\n".join(f"  {i+1}. {step}" for i, step in enumerate(val))
        return f"- **Description / Steps to Reproduce:**\n{body}"
    return f"- **Description / Steps to Reproduce:** {val}"

def _block_field(label, value, indent="  "):
    """Render a possibly multi-line value under a bulleted label.

    A fenced code block only renders if its fence starts its own line, and it
    only stays inside the list item if it is indented to the item's content
    column. A single-line value stays inline for compactness.
    """
    text = "" if value is None else str(value)
    if "\n" not in text:
        return f"- **{label}:** {text}"
    body = "\n".join(indent + ln if ln.strip() else "" for ln in text.splitlines())
    return f"- **{label}:**\n\n{body}"


def _finding_block(fnd):
    out = [f"## ID: {fnd['id']} — {fnd['title']}"]
    if fnd.get("code_severity") and fnd.get("effective_severity"):
        out.append(f"- **Code Severity:** {fnd['code_severity']} · **CVSS3:** "
                   f"{fnd.get('cvss3_score','N/A')} — `{fnd.get('cvss3_vector','')}`")
        out.append(f"- **Live/effective severity:** {fnd['effective_severity']}")
    else:
        out.append(f"- **Severity:** {fnd['severity']} · **CVSS3:** "
                   f"{fnd.get('cvss3_score','N/A')} — `{fnd.get('cvss3_vector','')}`")
    out.append(f"- **Short Description:** {fnd['short_description']}")
    out.append(_snippet_lines(fnd))
    out.append(_repro(fnd))
    if fnd.get("verification_note"):
        out.append(_block_field("Verification note", fnd["verification_note"]))
    out.append(_block_field("Suggested Fix", fnd["suggested_fix"]))
    return "\n".join(out)

def render(data):
    bands = _by_band(data["findings"])
    out = [_header(data), ""]
    for s in constants.SEVERITY_ORDER:
        if not bands[s]:
            continue
        out.append(f"# {s.upper()}\n")
        for fnd in bands[s]:
            out.append(_finding_block(fnd))
            out.append("")
    if data.get("meta", {}).get("sast_summary"):
        out.append("---\n")
        out.append("## Appendix — SAST / Dependency Pass\n")
        out.append(data["meta"]["sast_summary"])
    return "\n".join(out).rstrip() + "\n"
