import os, tempfile, json, unittest
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import detect

class TestDetect(unittest.TestCase):
    def test_npm_and_composer(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "package.json"), "w") as f:
                json.dump({"dependencies": {"express": "^4"}}, f)
            open(os.path.join(d, "composer.json"), "w").close()
            r = detect.detect_stack(d)
            self.assertEqual(r["package_managers"], ["composer", "npm"])
            self.assertIn("file:package.json", r["signals"])

    def test_python_manifests_collapse_to_pip(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "requirements.txt"), "w").close()
            open(os.path.join(d, "pyproject.toml"), "w").close()
            self.assertEqual(detect.detect_stack(d)["package_managers"], ["pip"])

    def test_empty_repo(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(detect.detect_stack(d), {"signals": [], "package_managers": []})

if __name__ == "__main__":
    unittest.main()
