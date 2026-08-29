import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StorageAndIsolationTests(unittest.TestCase):
    def test_required_storage_layers_are_documented(self):
        text = (ROOT / "docs" / "contracts" / "STORAGE_LAYERS_v0.1.md").read_text()
        for marker in ("RAW", "DERIVED", "MODEL", "append-only", "content hash"):
            self.assertIn(marker, text)

    def test_architecture_forbids_silent_cross_project_import(self):
        text = (ROOT / "docs" / "architecture" / "W0_ARCHITECTURE_v0.1.md").read_text()
        self.assertIn("TS.01", text)
        self.assertIn("TS.02", text)
        self.assertIn("No code, evidence, lock, parent", text)


if __name__ == "__main__":
    unittest.main()
