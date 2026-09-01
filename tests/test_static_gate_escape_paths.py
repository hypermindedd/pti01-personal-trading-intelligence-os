import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StaticGateEscapeTests(unittest.TestCase):
    def test_surface_registry_is_default_deny_and_complete(self):
        registry = json.loads(
            (ROOT / "config/source_surface_registry.v0.1.json").read_text()
        )
        self.assertEqual(registry["default_decision"], "DENY")
        required = {"python", "scripts", "tests", "mql5", ".github"}
        self.assertTrue(required.issubset(registry["classified_roots"]))

    def test_pull_requests_are_not_path_filtered(self):
        workflow = (ROOT / ".github/workflows/w0-contract-gate.yml").read_text()
        block = workflow.split("pull_request:", 1)[1].split("push:", 1)[0]
        self.assertNotIn("paths:", block)

    def test_mutation_probes_fail_in_every_executable_surface(self):
        sys_path = str(ROOT / "scripts")
        import sys
        sys.path.insert(0, sys_path)
        try:
            import w0_gate
            registry = json.loads(
                (ROOT / "config/source_surface_registry.v0.1.json").read_text()
            )
            probes = {
                "python/_probe.py": "mt5." + "order_send(request)",
                "python/_probe.pyw": "mt5." + "order_send(request)",
                "python/_probe.js": "mt5." + "order_send(request)",
                "python/_probe": "#!/usr/bin/env python\nmt5." + "order_send(request)",
                "scripts/_probe.py": "mt5." + "order_send(request)",
                "tests/_probe.py": "mt5." + "order_send(request)",
                "mql5/_probe.mq5": "Object" + "Create(0,x,OBJ_TREND,0,0,0);",
            }
            paths = []
            for relative, content in probes.items():
                path = ROOT / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
                paths.append(path)
            hits = w0_gate.scan_for_mutation_surface(registry)
            hit_paths = {hit["path"] for hit in hits}
            self.assertEqual(hit_paths, set(probes))
        finally:
            for path in locals().get("paths", []):
                path.unlink(missing_ok=True)
            sys.path.remove(sys_path)

    def test_unknown_extension_in_runtime_root_fails_closed(self):
        sys_path = str(ROOT / "scripts")
        import sys
        sys.path.insert(0, sys_path)
        path = ROOT / "python/_unknown.runtime"
        try:
            import w0_gate
            registry = json.loads(
                (ROOT / "config/source_surface_registry.v0.1.json").read_text()
            )
            path.write_text("safe-looking content", encoding="utf-8")
            self.assertIn(
                "python/_unknown.runtime",
                w0_gate.suspect_runtime_files(registry),
            )
        finally:
            path.unlink(missing_ok=True)
            sys.path.remove(sys_path)

    def test_only_empty_gitkeep_is_exempt(self):
        sys_path = str(ROOT / "scripts")
        import sys
        sys.path.insert(0, sys_path)
        path = ROOT / "python/_w_d/.gitkeep"
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            import w0_gate
            registry = json.loads(
                (ROOT / "config/source_surface_registry.v0.1.json").read_text()
            )
            path.write_text("", encoding="utf-8")
            self.assertNotIn(
                "python/_w_d/.gitkeep",
                w0_gate.suspect_runtime_files(registry),
            )
            path.write_text("#!/usr/bin/env python\n", encoding="utf-8")
            self.assertIn(
                "python/_w_d/.gitkeep",
                w0_gate.suspect_runtime_files(registry),
            )
        finally:
            path.unlink(missing_ok=True)
            path.parent.rmdir()
            sys.path.remove(sys_path)


if __name__ == "__main__":
    unittest.main()
