import os, unittest
from reportgen import schema, tsv, constants

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures", "sample_findings.json")

class TestTsv(unittest.TestCase):
    def setUp(self):
        self.data = schema.load(FIX)
        self.text = tsv.render(self.data)
        self.lines = self.text.rstrip("\n").split("\n")

    def test_header_is_11_columns(self):
        header = self.lines[0].split("\t")
        self.assertEqual(header, constants.TSV_COLUMNS)

    def test_row_count(self):
        self.assertEqual(len(self.lines), 1 + len(self.data["findings"]))

    def test_every_row_has_11_cells(self):
        for line in self.lines:
            self.assertEqual(len(line.split("\t")), 11)

    def test_literals_and_mapping(self):
        row1 = self.lines[1].split("\t")
        self.assertEqual(row1[0], "1")                       # ID
        self.assertEqual(row1[4], "Add screenshot here")     # Screenshot
        self.assertEqual(row1[5], "Open")                    # Status
        self.assertEqual(row1[6], "Critical")                # Severity
        self.assertEqual(row1[7], "22/07/2026")              # Date Reported
        self.assertEqual(row1[8], "")                        # Date Resolved
        self.assertEqual(row1[9], "Automated Security Audit (Claude Code)")

    def test_severity_note_appended(self):
        row3 = self.lines[2].split("\t")
        self.assertEqual(row3[6], "High (runtime-mitigated)")

    def test_description_cell_has_location_prefix_and_no_tabs_or_newlines(self):
        row1 = self.lines[1].split("\t")
        desc = row1[10]
        self.assertTrue(desc.startswith("Location/Evidence:"))
        self.assertNotIn("\n", desc)
        self.assertIn("src/routes/coupons.js:25", desc)

    def test_snippet_with_newline_and_tab_is_flattened(self):
        """Test that snippets with embedded newlines and tabs are flattened in TSV output."""
        # Create a finding with a snippet containing both newline and tab
        finding_with_problematic_snippet = {
            "meta": {
                "date_reported": "22/07/2026"
            },
            "findings": [
                {
                    "id": 99,
                    "bug_type": "Test Bug",
                    "short_description": "Test description",
                    "suggested_fix": "Test fix",
                    "severity": "High",
                    "locations": [
                        {
                            "file": "test/file.js",
                            "line": 42,
                            "snippet": "line1\nline2\tindented"
                        }
                    ],
                    "description_repro": "Test repro"
                }
            ]
        }

        text = tsv.render(finding_with_problematic_snippet)
        lines = text.rstrip("\n").split("\n")

        # Assert the number of physical lines is correct (1 header + 1 finding)
        self.assertEqual(len(lines), 2, f"Expected 2 lines (header + 1 finding), got {len(lines)}")

        # Assert every line has exactly 11 cells
        for i, line in enumerate(lines):
            cells = line.split("\t")
            self.assertEqual(
                len(cells), 11,
                f"Line {i} has {len(cells)} cells, expected 11. Line: {repr(line)}"
            )

        # Assert the description cell contains no newlines or tabs
        row = lines[1].split("\t")
        desc_cell = row[10]
        self.assertNotIn("\n", desc_cell, "Description cell should not contain newlines")
        self.assertNotIn("\t", desc_cell, "Description cell should not contain tabs")

if __name__ == "__main__":
    unittest.main()
