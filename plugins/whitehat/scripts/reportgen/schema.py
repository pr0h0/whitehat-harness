import json
from reportgen import constants

class SchemaError(Exception):
    pass

REQUIRED_FINDING_FIELDS = (
    "id", "title", "bug_type", "category", "severity",
    "short_description", "locations", "description_repro", "suggested_fix",
)

def load(path):
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, dict) or "findings" not in data:
        raise SchemaError("findings.json must be an object with a 'findings' array")
    data.setdefault("meta", {})
    if not isinstance(data["findings"], list):
        raise SchemaError("'findings' must be a list")
    seen_ids = set()
    for i, fnd in enumerate(data["findings"]):
        if not isinstance(fnd, dict):
            raise SchemaError(f"finding[{i}] must be an object")
        for field in REQUIRED_FINDING_FIELDS:
            if field not in fnd:
                raise SchemaError(f"finding[{i}] missing required field '{field}'")
        if fnd["severity"] not in constants.SEVERITY_ORDER:
            raise SchemaError(
                f"finding[{i}] severity '{fnd['severity']}' not one of {constants.SEVERITY_ORDER}")
        if fnd["category"] not in constants.AREAS:
            raise SchemaError(
                f"finding[{i}] category '{fnd['category']}' not one of the 11 areas")
        if fnd["id"] in seen_ids:
            raise SchemaError(f"duplicate finding id {fnd['id']}")
        seen_ids.add(fnd["id"])
        if not isinstance(fnd["locations"], list):
            raise SchemaError(f"finding[{i}] 'locations' must be a list")
    return data
