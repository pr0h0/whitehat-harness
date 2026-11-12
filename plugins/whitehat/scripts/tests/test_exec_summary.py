import os, unittest
from reportgen import schema, exec_summary

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures", "sample_findings.json")

class TestExecSummary(unittest.TestCase):
    def setUp(self):
        self.data = schema.load(FIX)
        self.md = exec_summary.render(self.data)

    def test_no_leftover_placeholders(self):
        self.assertNotIn("{{", self.md)
        self.assertNotIn("}}", self.md)

    def test_project_and_summary(self):
        self.assertIn("SampleApp", self.md)
        self.assertIn("Overall posture is mixed", self.md)

    def test_overall_assessment_has_all_areas(self):
        self.assertIn("# Executive Summary", self.md)
        self.assertIn("## Overall Assessment", self.md)
        self.assertIn("| **Secrets & Env Vars** |", self.md)
        self.assertIn("| **Information Disclosure** |", self.md)

    def test_prioritized_findings_ordered(self):
        self.assertIn("# Prioritized Findings", self.md)
        crit = self.md.index("Broken Authentication")
        sqli = self.md.index("SQL Injection")
        self.assertLess(crit, sqli)  # Critical before High

    def test_remediation_guide(self):
        self.assertIn("# Appendix: Remediation Guide", self.md)
        self.assertIn("Authenticate the signing endpoint", self.md)

    def test_prioritized_findings_uses_short_description(self):
        """Test that Prioritized Findings table uses full short_description instead of title."""
        # This substring from finding 1's short_description is NOT in its title
        self.assertIn("An unauthenticated endpoint signs an attacker-supplied discount token", self.md)

if __name__ == "__main__":
    unittest.main()
