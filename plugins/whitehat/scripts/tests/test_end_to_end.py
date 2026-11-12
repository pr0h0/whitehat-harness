import os, tempfile, unittest
from reportgen import cli

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures", "sample_findings.json")
ROOT = os.path.dirname(os.path.dirname(HERE))

class TestEndToEnd(unittest.TestCase):
    def test_fixture_produces_three_nonempty_files(self):
        with tempfile.TemporaryDirectory() as d:
            paths = cli.generate(FIX, d, "sampleapp")
            for key in ("tsv", "detailed_md", "exec_summary"):
                self.assertGreater(os.path.getsize(paths[key]), 200, key)

    def test_audit_skill_exists(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, "skills", "audit", "SKILL.md")))

if __name__ == "__main__":
    unittest.main()
