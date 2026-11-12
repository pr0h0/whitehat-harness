# scripts/tests/test_cli.py
import os, tempfile, unittest
from reportgen import cli

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures", "sample_findings.json")

class TestCli(unittest.TestCase):
    def test_generate_writes_three_files(self):
        with tempfile.TemporaryDirectory() as d:
            paths = cli.generate(FIX, d, "sampleapp")
            self.assertTrue(os.path.exists(paths["tsv"]))
            self.assertTrue(os.path.exists(paths["detailed_md"]))
            self.assertTrue(os.path.exists(paths["exec_summary"]))
            self.assertTrue(paths["tsv"].endswith("sampleapp_findings.tsv"))
            with open(paths["tsv"]) as f:
                self.assertIn("\t", f.readline())

    def test_detailed_md_filename_uses_audit_date(self):
        with tempfile.TemporaryDirectory() as d:
            paths = cli.generate(FIX, d, "sampleapp")
            self.assertTrue(os.path.basename(paths["detailed_md"])
                            .startswith("SECURITY_AUDIT_2026_07_23"))

    def test_cli_runs_as_script_by_path(self):
        import subprocess, sys, os
        scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cli_path = os.path.join(scripts_dir, "reportgen", "cli.py")
        with tempfile.TemporaryDirectory() as d:
            # run from a cwd that is NOT scripts/, invoking by absolute path
            proc = subprocess.run(
                [sys.executable, cli_path, FIX, "--out", d, "--slug", "probe"],
                cwd=d, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(os.path.exists(os.path.join(d, "probe_findings.tsv")))

if __name__ == "__main__":
    unittest.main()
