import re

from reportgen import constants

_FENCE = re.compile(r"```[A-Za-z0-9+#-]*\s*\n(.*?)```", re.S)


def _cell(text):
    """Render arbitrary text safely inside a GitHub-flavoured markdown table cell.

    A table cell cannot contain a raw newline or a fenced code block -- either one
    terminates the row and corrupts the remainder of the document. Fences become
    inline code spans, newlines become <br>, and pipes are escaped.
    """
    if text is None:
        return ""

    def _fence_to_inline(match):
        lines = [ln.strip() for ln in match.group(1).splitlines() if ln.strip()]
        return " " + "<br>".join(f"`{ln}`" for ln in lines) + " "

    s = _FENCE.sub(_fence_to_inline, str(text))
    s = s.replace("|", "\\|")
    s = re.sub(r"\s*\n\s*", "<br>", s.strip())
    return re.sub(r"(?:<br>)+", "<br>", s)


def _sev_rank(fnd):
    return constants.SEVERITY_ORDER.index(fnd["severity"])

def _first_location(fnd):
    locs = fnd.get("locations", [])
    if not locs:
        return ""
    loc = locs[0]
    return f"{loc['file']}:{loc.get('line')}" if loc.get("line") is not None else loc["file"]

def render(data):
    meta = data.get("meta", {})
    findings = data["findings"]
    name = meta.get("project_name", "Application")
    org = meta.get("organization", "Internal")
    date = meta.get("audit_date", "")
    out = []
    out.append(f"**{name}**\n")
    out.append("**Security Audit Report**\n")
    out.append(f"*{date}  |  {org}*\n")
    out.append("# Executive Summary\n")
    out.append(f"A security audit of the {name} codebase was conducted on {date}. "
               "The audit covered secret management, authentication, session security, CORS, "
               "database access, input validation, third-party integrations, dependencies, "
               "rate limiting, denial of service, and information disclosure.\n")
    out.append(meta.get("summary_paragraph", "") + "\n")

    # Overall Assessment
    out.append("## Overall Assessment\n")
    out.append("| Area | Result | Summary |")
    out.append("| :---- | :---: | :---- |")
    assessments = {a["area"]: a for a in meta.get("area_assessments", [])}
    for area in constants.AREAS:
        a = assessments.get(area, {"result": "—", "summary": ""})
        out.append(f"| **{area}** | **{a['result']}** | {_cell(a['summary'])} |")

    # Finding Summary by Category
    out.append("\n# Finding Summary by Category\n")
    out.append("| Category | Findings | Critical/High | Status |")
    out.append("| :---- | :---: | :---: | :---: |")
    for area in constants.AREAS:
        cat = [f for f in findings if f["category"] == area]
        if not cat:
            continue
        ch = sum(1 for f in cat if f["severity"] in ("Critical", "High"))
        status = "Needs Fix" if ch else "Good"
        out.append(f"| {area} | {len(cat)} | {ch} | **{status}** |")

    # Prioritized Findings
    out.append("\n# Prioritized Findings\n")
    out.append("All findings ordered by severity and risk impact.\n")
    out.append("| # | Severity | Location | Finding | Fix |")
    out.append("| :---: | :---: | :---- | :---- | :---- |")
    for fnd in sorted(findings, key=lambda f: (_sev_rank(f), f["id"])):
        out.append(f"| **{fnd['id']}** | **{fnd['severity']}** | `{_first_location(fnd)}` | "
                   f"{_cell(fnd['bug_type'] + ': ' + fnd['short_description'])} | "
                   f"{_cell(fnd['suggested_fix'])} |")

    # Remediation Guide
    out.append("\n# Appendix: Remediation Guide\n")
    for i, step in enumerate(meta.get("remediation_steps", []), 1):
        est = f" ({step['estimate']})" if step.get("estimate") else ""
        out.append(f"## Step {i} — {step.get('title','')}{est}\n")
        if step.get("summary"):
            out.append(step["summary"] + "\n")
        for instr in step.get("instructions", []):
            out.append(f"- {instr}")
        out.append("")

    out.append("---\n")
    out.append(f"*{name} Security Audit — {date}  |  {org}*")
    return "\n".join(out).rstrip() + "\n"
