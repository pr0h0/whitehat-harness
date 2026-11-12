from reportgen import constants

def _flatten(value):
    if isinstance(value, list):
        return " ".join(_flatten(v) for v in value)
    return str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ").strip()

def _severity_cell(fnd):
    sev = fnd["severity"]
    note = fnd.get("severity_note")
    return f"{sev} ({note})" if note else sev

def _locations_str(fnd):
    parts = []
    for loc in fnd.get("locations", []):
        line = loc.get("line")
        flat_file = _flatten(loc.get('file', ''))
        ref = f"{flat_file}:{line}" if line is not None else flat_file
        snip = loc.get("snippet")
        flat_snip = _flatten(snip) if snip else None
        parts.append(f"{ref} — {flat_snip}" if flat_snip else ref)
    return "; ".join(parts)

def _description_cell(fnd):
    pieces = ["Location/Evidence: " + _locations_str(fnd)]
    pieces.append(_flatten(fnd["description_repro"]))
    if fnd.get("verification_note"):
        pieces.append(_flatten(fnd["verification_note"]))
    return " ".join(p for p in pieces if p).replace("\t", " ")

def _row(fnd, meta):
    d = constants.DEFAULTS
    return [
        str(fnd["id"]),
        _flatten(fnd["bug_type"]),
        _flatten(fnd["short_description"]),
        _flatten(fnd["suggested_fix"]),
        d["screenshot"],
        fnd.get("status", d["status"]),
        _severity_cell(fnd),
        fnd.get("date_reported", meta.get("date_reported", "")),
        fnd.get("date_resolved", ""),
        fnd.get("reported_by", d["reported_by"]),
        _description_cell(fnd),
    ]

def render(data):
    meta = data.get("meta", {})
    lines = ["\t".join(constants.TSV_COLUMNS)]
    for fnd in data["findings"]:
        lines.append("\t".join(_row(fnd, meta)))
    return "\n".join(lines) + "\n"
