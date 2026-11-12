AREAS = [
    "Secrets & Env Vars",
    "Auth & Authorization",
    "Session Security",
    "CORS",
    "Database",
    "Input Validation",
    "Third-Party Integrations",
    "Dependencies",
    "Rate Limiting",
    "DoS",
    "Information Disclosure",
]

SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Informational"]

TSV_COLUMNS = [
    "ID", "Bug Type", "Short Description", "Suggested fix", "Screenshot",
    "Status", "Severity", "Date Reported", "Date Resolved", "Reported By",
    "Description/Steps to reproduce",
]

DEFAULTS = {
    "screenshot": "Add screenshot here",
    "status": "Open",
    "reported_by": "Automated Security Audit (Claude Code)",
}
