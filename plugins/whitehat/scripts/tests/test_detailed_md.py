import os, unittest
from reportgen import schema, detailed_md

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures", "sample_findings.json")

class TestDetailedMd(unittest.TestCase):
    def setUp(self):
        self.data = schema.load(FIX)
        self.md = detailed_md.render(self.data)

    def test_has_severity_bands_in_order(self):
        self.assertIn("# CRITICAL", self.md)
        self.assertIn("# HIGH", self.md)
        self.assertLess(self.md.index("# CRITICAL"), self.md.index("# HIGH"))

    def test_finding_blocks(self):
        self.assertIn("## ID: 1 — Broken Authentication -> Signed-Coupon Forgery", self.md)
        self.assertIn("**CVSS3:** 9.0 — `AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N`", self.md)
        self.assertIn("**Short Description:**", self.md)
        self.assertIn("**Vulnerable Code Snippet:**", self.md)
        self.assertIn("`src/routes/coupons.js:25`", self.md)
        self.assertIn("**Suggested Fix:**", self.md)

    def test_numbered_repro_steps(self):
        self.assertIn("  1. The checkout accepts a discount", self.md)

    def test_split_severity_rendered(self):
        self.assertIn("**Code Severity:** High", self.md)
        self.assertIn("**Live/effective severity:** Low-Medium (mitigated)", self.md)

    def test_verification_note_rendered(self):
        self.assertIn("**Verification note:**", self.md)
        self.assertIn("A WAF in front of the app", self.md)

    def test_summary_table_and_scope(self):
        self.assertIn("## Summary", self.md)
        self.assertIn("| Critical | 1 |", self.md)
        self.assertIn("backend — Node.js API", self.md)

    def test_empty_band_omitted(self):
        self.assertNotIn("# INFORMATIONAL", self.md)

if __name__ == "__main__":
    unittest.main()
