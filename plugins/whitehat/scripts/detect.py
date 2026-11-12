import argparse, json, os

# manifest file -> package manager / SAST tooling to run (see references/sast-tools.md)
MANIFESTS = {
    "package.json": "npm",
    "composer.json": "composer",
    "requirements.txt": "pip",
    "pyproject.toml": "pip",
    "Pipfile": "pip",
    "go.mod": "go",
    "Gemfile": "bundler",
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "Cargo.toml": "cargo",
}

def detect_stack(root):
    found = [(name, pm) for name, pm in MANIFESTS.items() if os.path.exists(os.path.join(root, name))]
    return {
        "signals": [f"file:{name}" for name, _ in found],
        "package_managers": sorted({pm for _, pm in found}),
    }

def main(argv=None):
    p = argparse.ArgumentParser(description="Detect package managers in an app")
    p.add_argument("root", nargs="?", default=".")
    args = p.parse_args(argv)
    print(json.dumps(detect_stack(args.root), indent=2))

if __name__ == "__main__":
    main()
