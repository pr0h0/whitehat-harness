import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reportgen import schema, tsv, detailed_md, exec_summary

def generate(findings_path, out_dir, app_slug):
    data = schema.load(findings_path)
    date = data.get("meta", {}).get("audit_date", "").replace("-", "_") or "UNDATED"
    os.makedirs(out_dir, exist_ok=True)
    paths = {
        "tsv": os.path.join(out_dir, f"{app_slug}_findings.tsv"),
        "detailed_md": os.path.join(out_dir, f"SECURITY_AUDIT_{date}.md"),
        "exec_summary": os.path.join(out_dir, f"{app_slug}_exec_summary.md"),
    }
    with open(paths["tsv"], "w") as f:
        f.write(tsv.render(data))
    with open(paths["detailed_md"], "w") as f:
        f.write(detailed_md.render(data))
    with open(paths["exec_summary"], "w") as f:
        f.write(exec_summary.render(data))
    return paths

def main(argv=None):
    p = argparse.ArgumentParser(description="Generate audit deliverables from findings.json")
    p.add_argument("findings", help="path to findings.json")
    p.add_argument("--out", default=".", help="output directory (default: cwd)")
    p.add_argument("--slug", required=True, help="app slug for filenames, e.g. sampleapp")
    args = p.parse_args(argv)
    paths = generate(args.findings, args.out, args.slug)
    for k, v in paths.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
