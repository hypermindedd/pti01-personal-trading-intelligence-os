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

    def test_reconciliation_never_rewrites_raw(self):
        text = (ROOT / "docs" / "contracts" / "FAILURE_RECONCILIATION_v0.1.md").read_text()
        for marker in ("Never edit, delete or reorder RAW", "UNEXPLAINED_DELTA", "source_instance_id"):
            self.assertIn(marker, text)

    def test_latent_rule_classes_are_not_silently_promoted(self):
        text = (ROOT / "docs" / "contracts" / "LATENT_RULE_EPISTEMICS_v0.1.md").read_text()
        for marker in ("REPEATED_BEHAVIOR", "INFERRED_RULE", "VALIDATED_EDGE", "No class may be silently promoted"):
            self.assertIn(marker, text)

    def test_w1_interface_remains_read_only(self):
        text = (ROOT / "docs" / "architecture" / "W0_W1_INTERFACE_FREEZE_v0.1.md").read_text()
        self.assertIn("Forbidden W1 surfaces", text)
        self.assertIn("Order/position/account mutation APIs", text)
        self.assertIn("HUMAN locks W0", text)

    def test_excluded_images_are_absent(self):
        excluded = {"IMG_2750.png", "IMG_2751.jpeg"}
        present = [p for p in ROOT.rglob("*") if p.is_file() and p.name in excluded]
        self.assertEqual([], present)


if __name__ == "__main__":
    unittest.main()
