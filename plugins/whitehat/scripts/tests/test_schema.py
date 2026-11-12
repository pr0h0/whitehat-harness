import os, json, unittest
from reportgen import schema, constants

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures", "sample_findings.json")

class TestSchema(unittest.TestCase):
    def test_areas_and_severities(self):
        self.assertEqual(len(constants.AREAS), 11)
        self.assertEqual(constants.AREAS[0], "Secrets & Env Vars")
        self.assertEqual(constants.SEVERITY_ORDER[0], "Critical")
        self.assertEqual(len(constants.TSV_COLUMNS), 11)

    def test_valid_fixture_loads(self):
        data = schema.load(FIX)
        self.assertIn("meta", data)
        self.assertIn("findings", data)
        self.assertEqual(data["findings"][0]["id"], 1)

    def test_bad_severity_rejected(self):
        bad = {"meta": {}, "findings": [{"id": 1, "severity": "Spicy",
                "title": "x", "bug_type": "x", "category": "CORS",
                "short_description": "x", "suggested_fix": "x",
                "locations": [], "description_repro": "x"}]}
        p = os.path.join(HERE, "fixtures", "_bad.json")
        with open(p, "w") as f: json.dump(bad, f)
        with self.assertRaises(schema.SchemaError):
            schema.load(p)
        os.remove(p)

    def test_bad_category_rejected(self):
        bad = {"meta": {}, "findings": [{"id": 1, "severity": "Low",
                "title": "x", "bug_type": "x", "category": "Nonsense",
                "short_description": "x", "suggested_fix": "x",
                "locations": [], "description_repro": "x"}]}
        p = os.path.join(HERE, "fixtures", "_bad2.json")
        with open(p, "w") as f: json.dump(bad, f)
        with self.assertRaises(schema.SchemaError):
            schema.load(p)
        os.remove(p)

    def test_duplicate_id_rejected(self):
        fnd = {"severity": "Low", "title": "x", "bug_type": "x",
               "category": "CORS", "short_description": "x", "suggested_fix": "x",
               "locations": [], "description_repro": "x"}
        bad = {"meta": {}, "findings": [
            {**fnd, "id": 1},
            {**fnd, "id": 1},
        ]}
        p = os.path.join(HERE, "fixtures", "_bad3.json")
        with open(p, "w") as f: json.dump(bad, f)
        with self.assertRaises(schema.SchemaError):
            schema.load(p)
        os.remove(p)

    def test_missing_required_field_rejected(self):
        bad = {"meta": {}, "findings": [{"id": 1, "severity": "Low",
                "title": "x", "bug_type": "x", "category": "CORS",
                "short_description": "x",
                "locations": [], "description_repro": "x"}]}  # missing suggested_fix
        p = os.path.join(HERE, "fixtures", "_bad4.json")
        with open(p, "w") as f: json.dump(bad, f)
        with self.assertRaises(schema.SchemaError):
            schema.load(p)
        os.remove(p)

    def test_non_dict_finding_rejected(self):
        bad = {"meta": {}, "findings": ["not-a-dict"]}
        p = os.path.join(HERE, "fixtures", "_bad5.json")
        with open(p, "w") as f: json.dump(bad, f)
        with self.assertRaises(schema.SchemaError):
            schema.load(p)
        os.remove(p)

if __name__ == "__main__":
    unittest.main()
