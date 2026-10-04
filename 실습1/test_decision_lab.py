import unittest
from types import SimpleNamespace
from unittest.mock import patch

import decision_lab as d

class DecisionLabTests(unittest.TestCase):
    def test_payload_uses_closed_questions(self):
        p = d.build_request("agent-gate", "git status", "ollama", "tev1:0.8b")
        self.assertEqual(p["model"], "tev1:0.8b")
        self.assertEqual(set(p["questions"]), {"action", "destructive", "exfiltration", "impact"})
        self.assertEqual(p["questions"]["action"]["type"], "choice")

    def test_mock_is_explicit(self):
        r = d.mock_response("agent-gate", "git status")
        self.assertEqual(r["model"], "rule-mock-not-jev")

    def test_safe_command_allowed(self):
        r = d.validate_response("agent-gate", d.mock_response("agent-gate", "git status"))
        self.assertEqual(d.apply_policy("agent-gate", r)["decision"], "ALLOW")

    def test_destructive_command_blocked(self):
        r = d.validate_response("agent-gate", d.mock_response("agent-gate", "rm -rf project"))
        self.assertEqual(d.apply_policy("agent-gate", r)["decision"], "BLOCK")

    def test_sensitive_ticket_reviewed(self):
        r = d.validate_response("ticket", d.mock_response("ticket", "비밀번호와 API key를 보냅니다"))
        self.assertEqual(d.apply_policy("ticket", r)["decision"], "REDACT_AND_REVIEW")

    def test_rejects_invented_choice(self):
        raw = d.mock_response("agent-gate", "git status")
        raw["answers"]["action"]["choice"] = "execute_everything"
        with self.assertRaises(ValueError): d.validate_response("agent-gate", raw)

    def test_noul_legacy_probability_supported(self):
        raw = d.mock_response("model-router", "요약")
        raw["answers"]["high_risk"] = {"probability": 0.2}
        r = d.validate_response("model-router", raw)
        self.assertEqual(r["answers"]["high_risk"]["probability"], 0.2)

if __name__ == "__main__": unittest.main()
