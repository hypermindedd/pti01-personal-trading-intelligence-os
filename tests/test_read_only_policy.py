import copy
import unittest
from pathlib import Path

from pti01.contracts import ContractViolation, load_json, validate_read_only_policy

ROOT = Path(__file__).resolve().parents[1]


class ReadOnlyPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_json(ROOT / "config" / "read_only_policy.v0.1.json")

    def test_policy_is_default_deny_and_read_only(self):
        validate_read_only_policy(self.policy)

    def test_execution_policy_fails_closed(self):
        policy = copy.deepcopy(self.policy)
        policy["mode"] = "EXECUTE"
        with self.assertRaisesRegex(ContractViolation, "READ_ONLY"):
            validate_read_only_policy(policy)

    def test_mutation_capability_cannot_enter_allow_set(self):
        policy = copy.deepcopy(self.policy)
        policy["allowed_capabilities"].append("broker.order_send")
        with self.assertRaises(ContractViolation):
            validate_read_only_policy(policy)

    def test_unknown_capability_aliases_fail_closed(self):
        for capability in ("execute.trade", "terminal.dispatch", "mt5.send"):
            with self.subTest(capability=capability):
                policy = copy.deepcopy(self.policy)
                policy["allowed_capabilities"].append(capability)
                with self.assertRaisesRegex(ContractViolation, "exact authority"):
                    validate_read_only_policy(policy)


if __name__ == "__main__":
    unittest.main()
