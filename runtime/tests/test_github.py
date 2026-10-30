import unittest
from specter_runtime.github.client import (
    GitHubClient,
    GitHubTokenVault,
    UnapprovedMutationError,
)

class TestGitHubIntegration(unittest.TestCase):
    def setUp(self):
        self.vault = GitHubTokenVault(token="ghp_super_secret_test_token_12345")
        self.client = GitHubClient(token_vault=self.vault)

    def test_token_vault_redaction(self):
        # Ensure string representation hides token
        self.assertNotIn("ghp_super_secret_test_token_12345", str(self.vault))
        self.assertNotIn("ghp_super_secret_test_token_12345", repr(self.vault))
        self.assertEqual(str(self.vault), "[REDACTED_TOKEN]")

    def test_read_issues_fixture(self):
        issues = self.client.list_issues("org/repo")
        self.assertGreaterEqual(len(issues), 1)
        issue_1 = self.client.get_issue("org/repo", 1)
        self.assertIsNotNone(issue_1)
        self.assertIn("Buffer underflow", issue_1.title)

    def test_branch_creation_requires_approval(self):
        with self.assertRaises(UnapprovedMutationError):
            self.client.create_branch("org/repo", "specter/fix-1", approval_status="PENDING")

        with self.assertRaises(UnapprovedMutationError):
            self.client.create_branch("org/repo", "specter/fix-1", approval_status="REJECTED")

        # Authorized when APPROVED
        res = self.client.create_branch("org/repo", "specter/fix-1", approval_status="APPROVED")
        self.assertEqual(res["status"], "created")
        self.assertEqual(res["branch"], "specter/fix-1")

    def test_pull_request_creation_requires_approval(self):
        with self.assertRaises(UnapprovedMutationError):
            self.client.create_pull_request(
                repo="org/repo",
                title="[SPECTER] Fix #1",
                body="Audit diff...",
                head_branch="specter/fix-1",
                base_branch="main",
                approval_status="PENDING",
            )

        # Authorized when APPROVED
        pr = self.client.create_pull_request(
            repo="org/repo",
            title="[SPECTER] Fix #1",
            body="Audit diff...",
            head_branch="specter/fix-1",
            base_branch="main",
            approval_status="APPROVED",
        )
        self.assertEqual(pr["status"], "created")
        self.assertIn("/pull/99", pr["html_url"])

if __name__ == "__main__":
    unittest.main()

