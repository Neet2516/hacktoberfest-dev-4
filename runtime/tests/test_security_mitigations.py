import unittest
from specter_runtime.github.client import GitHubTokenVault, UnapprovedMutationError, GitHubClient
from specter_runtime.review.reviewer import SecurityScanner
from specter_runtime.testing.sandbox_runner import DockerTestSandbox

class TestSecurityMitigations(unittest.TestCase):
    def test_credential_leak_detection_in_diff(self):
        malicious_diff = """--- a/src/auth.py
+++ b/src/auth.py
@@ -1,2 +1,3 @@
+api_key = "ghp_super_secret_admin_token_abcdef123456"
"""
        findings = SecurityScanner.scan_diff(malicious_diff, "src/auth.py")
        self.assertTrue(any(f.category == "SECURITY" and f.severity == "BLOCKER" for f in findings))

    def test_unsafe_dynamic_execution_detection(self):
        malicious_diff = """--- a/src/handler.py
+++ b/src/handler.py
@@ -10,1 +10,2 @@
+eval(user_submitted_code)
"""
        findings = SecurityScanner.scan_diff(malicious_diff, "src/handler.py")
        self.assertTrue(any("eval()" in f.description for f in findings))

    def test_sandbox_network_isolation_flag(self):
        sandbox = DockerTestSandbox()
        cmd = sandbox.build_docker_command("/workspace", ["test"])
        idx = cmd.index("--network")
        self.assertEqual(cmd[idx + 1], "none", "Sandbox container MUST have networking disabled (--network none)")

    def test_sandbox_readonly_mount(self):
        sandbox = DockerTestSandbox()
        cmd = sandbox.build_docker_command("/workspace/dir", ["cargo", "test"])
        self.assertTrue(any(":ro" in arg for arg in cmd), "Host workspace volume MUST be mounted read-only (:ro)")

    def test_github_token_vault_redaction(self):
        vault = GitHubTokenVault(token="ghp_very_confidential_token_9999")
        self.assertEqual(str(vault), "[REDACTED_TOKEN]")
        self.assertNotIn("ghp_very_confidential_token_9999", repr(vault))

    def test_unauthorized_vcs_mutation_prevention(self):
        client = GitHubClient()
        with self.assertRaises(UnapprovedMutationError):
            client.create_pull_request(
                repo="test/repo",
                title="Bypassing human review",
                body="malicious",
                head_branch="patch",
                base_branch="main",
                approval_status="UNAPPROVED",
            )

if __name__ == "__main__":
    unittest.main()
