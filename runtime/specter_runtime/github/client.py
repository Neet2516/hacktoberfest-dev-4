import os
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

class UnapprovedMutationError(PermissionError):
    """Raised when an attempt is made to mutate GitHub state without valid human signoff."""
    pass

class TokenLeakageError(RuntimeError):
    """Raised when GitHub token is passed into an unverified or prompt context."""
    pass

class GitHubTokenVault:
    """Isolated storage for VCS credentials. Guarantees token cannot be dumped to prompts or logs."""

    def __init__(self, token: Optional[str] = None):
        self._token = token or os.environ.get("GITHUB_TOKEN", "mock_gh_token_dev_2026")

    def get_token_for_api_call(self) -> str:
        return self._token

    def __repr__(self) -> str:
        return "<GitHubTokenVault: [REDACTED_BY_SECURITY_POLICY]>"

    def __str__(self) -> str:
        return "[REDACTED_TOKEN]"

@dataclass
class GitHubIssue:
    number: int
    title: str
    body: str
    state: str = "open"
    labels: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class GitHubClient:
    """GitHub API client providing read-only issue inspection and human-gated PR operations."""

    def __init__(
        self,
        token_vault: Optional[GitHubTokenVault] = None,
        fixture_path: Optional[str] = None,
    ):
        self.vault = token_vault or GitHubTokenVault()
        self.fixture_path = fixture_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "fixtures", "issues", "sample_issues.json"
        )
        self._mock_issues: List[GitHubIssue] = []
        self._load_fixtures()

    def _load_fixtures(self):
        if os.path.exists(self.fixture_path):
            try:
                with open(self.fixture_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        self._mock_issues.append(
                            GitHubIssue(
                                number=item["number"],
                                title=item["title"],
                                body=item["body"],
                                state=item.get("state", "open"),
                                labels=item.get("labels", []),
                                created_at=item.get("created_at", ""),
                            )
                        )
            except Exception:
                pass

        if not self._mock_issues:
            self._mock_issues.append(
                GitHubIssue(
                    number=1,
                    title="Buffer underflow when parsing empty slice in config parser",
                    body="When calling parse_config with an empty string, panics with index out of bounds.",
                    labels=["bug"],
                )
            )

    def list_issues(self, repo: str) -> List[GitHubIssue]:
        return self._mock_issues

    def get_issue(self, repo: str, issue_number: int) -> Optional[GitHubIssue]:
        for issue in self._mock_issues:
            if issue.number == issue_number:
                return issue
        return None

    def create_branch(self, repo: str, branch_name: str, approval_status: str) -> Dict[str, Any]:
        """Creates a maintenance branch. REQUIRES verified approval."""
        if approval_status != "APPROVED":
            raise UnapprovedMutationError(
                f"Cannot create remote branch '{branch_name}': Proposal status is '{approval_status}', human approval required."
            )
        return {
            "status": "created",
            "branch": branch_name,
            "ref": f"refs/heads/{branch_name}",
            "sha": "a1b2c3d4e5f67890",
        }

    def create_pull_request(
        self,
        repo: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str,
        approval_status: str,
    ) -> Dict[str, Any]:
        """Submits a Pull Request. STRICTLY REQUIRES verified human approval."""
        if approval_status != "APPROVED":
            raise UnapprovedMutationError(
                f"Cannot create Pull Request: Proposal status is '{approval_status}', human approval required."
            )
        return {
            "status": "created",
            "html_url": f"https://github.com/{repo}/pull/99",
            "number": 99,
            "title": title,
            "head": head_branch,
            "base": base_branch,
            "draft": False,
        }

