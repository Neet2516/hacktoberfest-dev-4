import unittest
import asyncio
from specter_runtime.context import AgentContext
from specter_runtime.message_bus import AgentMessageBus
from specter_runtime.review.reviewer import (
    SecurityScanner,
    AdversarialReviewerAgent,
    ReviewVerdictReport,
)

class DummyLLM:
    def generate(self, prompt: str, system: str = "") -> str:
        return "Adversarial audit completed: No critical logic flaws detected."

class TestAdversarialReviewer(unittest.TestCase):
    def setUp(self):
        self.message_bus = AgentMessageBus()
        self.dummy_llm = DummyLLM()
        self.agent = AdversarialReviewerAgent(
            agent_id="test_reviewer",
            message_bus=self.message_bus,
            ollama_client=self.dummy_llm,
        )

    def test_security_scanner_clean_diff(self):
        diff = """--- a/src/lib.rs
+++ b/src/lib.rs
@@ -1,3 +1,4 @@
+fn add(a: i32, b: i32) -> i32 { a + b }
"""
        findings = SecurityScanner.scan_diff(diff, "src/lib.rs")
        self.assertEqual(len(findings), 0)

    def test_security_scanner_detects_credentials(self):
        diff = """--- a/src/config.py
+++ b/src/config.py
@@ -10,2 +10,3 @@
+api_key = "secret_token_1234567890abcdef"
"""
        findings = SecurityScanner.scan_diff(diff, "src/config.py")
        self.assertGreaterEqual(len(findings), 1)
        self.assertEqual(findings[0].category, "SECURITY")
        self.assertEqual(findings[0].severity, "BLOCKER")

    def test_security_scanner_detects_eval(self):
        diff = """--- a/src/app.js
+++ b/src/app.js
@@ -5,2 +5,3 @@
+const res = eval(userInput);
"""
        findings = SecurityScanner.scan_diff(diff, "src/app.js")
        self.assertGreaterEqual(len(findings), 1)
        self.assertIn("eval()", findings[0].description)

    def test_reviewer_approved_flow(self):
        clean_diff = """--- a/src/calc.py
+++ b/src/calc.py
@@ -1,3 +1,4 @@
+def multiply(x, y):
+    return x * y
"""
        context = AgentContext(
            task_id="task_rev_001",
            repository_url="https://github.com/test/repo",
            workspace_path="/tmp/workspace",
            parameters={
                "diff_content": clean_diff,
                "target_file": "src/calc.py",
            },
        )
        result = asyncio.run(self.agent.run(context))
        self.assertTrue(result.data["approved"])
        self.assertEqual(result.data["verdict"], "APPROVED")
        self.assertEqual(result.data["regression_risk"], "LOW")

    def test_reviewer_rejected_unsafe_flow(self):
        unsafe_diff = """--- a/src/secrets.py
+++ b/src/secrets.py
@@ -1,2 +1,3 @@
+password = "supersecretmasterkey99999"
"""
        context = AgentContext(
            task_id="task_rev_002",
            repository_url="https://github.com/test/repo",
            workspace_path="/tmp/workspace",
            parameters={
                "diff_content": unsafe_diff,
                "target_file": "src/secrets.py",
            },
        )
        result = asyncio.run(self.agent.run(context))
        self.assertFalse(result.data["approved"])
        self.assertEqual(result.data["verdict"], "REJECTED_UNSAFE")
        self.assertEqual(result.data["security_risk"], "CRITICAL")

if __name__ == "__main__":
    unittest.main()
