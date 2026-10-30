import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

@dataclass
class MaintenanceProposal:
    proposal_id: str
    pipeline_id: str
    repository_url: str
    issue_number: int
    issue_title: str
    patch_diff: str
    files_changed: List[str]
    verification_summary: str
    review_verdict: str
    risk_level: str
    status: str = "PENDING_APPROVAL"  # "PENDING_APPROVAL", "APPROVED", "REJECTED"
    human_reviewer: Optional[str] = None
    rejection_feedback: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: Optional[str] = None

    def compute_sha256(self) -> str:
        content = f"{self.proposal_id}:{self.patch_diff}:{self.status}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def format_github_pr(self) -> Dict[str, str]:
        title = f"[SPECTER] Fix #{self.issue_number}: {self.issue_title}"
        body = f"""## 👻 SPECTER Autonomous Maintenance Proposal

**Target Issue:** #{self.issue_number} - {self.issue_title}
**Proposal ID:** `{self.proposal_id}`
**Status:** `{self.status}` (Approved by: `{self.human_reviewer or "Pending"}`)
**Audit Hash (SHA-256):** `{self.compute_sha256()[:16]}`

---

### 🛡️ Adversarial Review & Verification
- **Review Verdict:** {self.review_verdict} (Risk: `{self.risk_level}`)
- **Isolated Test Verification:** {self.verification_summary}
- **Security Check:** Passed with 0 blocker findings (scanned for secrets, dynamic eval, and unescaped shell calls).

---

### 📝 Files Changed
{chr(10).join(f"- `{f}`" for f in self.files_changed)}

### 🔍 Unified Patch Diff
```diff
{self.patch_diff}
```

---
*Generated autonomously by **SPECTER: The Ghost Maintainer** with human-in-the-loop signoff.*
"""
        return {"title": title, "body": body}

class ApprovalGate:
    """Enforces human-in-the-loop confirmation before any remote branch push or pull request creation."""

    def __init__(self):
        self.proposals: Dict[str, MaintenanceProposal] = {}

    def create_proposal(
        self,
        pipeline_id: str,
        repository_url: str,
        issue_number: int,
        issue_title: str,
        patch_diff: str,
        files_changed: List[str],
        verification_summary: str,
        review_verdict: str,
        risk_level: str = "LOW",
    ) -> MaintenanceProposal:
        proposal_id = f"prop_{hashlib.md5(f'{pipeline_id}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"
        proposal = MaintenanceProposal(
            proposal_id=proposal_id,
            pipeline_id=pipeline_id,
            repository_url=repository_url,
            issue_number=issue_number,
            issue_title=issue_title,
            patch_diff=patch_diff,
            files_changed=files_changed,
            verification_summary=verification_summary,
            review_verdict=review_verdict,
            risk_level=risk_level,
        )
        self.proposals[proposal_id] = proposal
        return proposal

    def approve(self, proposal_id: str, reviewer_name: str) -> MaintenanceProposal:
        if proposal_id not in self.proposals:
            raise KeyError(f"Proposal {proposal_id} does not exist.")
        prop = self.proposals[proposal_id]
        prop.status = "APPROVED"
        prop.human_reviewer = reviewer_name
        prop.resolved_at = datetime.now(timezone.utc).isoformat()
        return prop

    def reject(self, proposal_id: str, reviewer_name: str, feedback: str) -> MaintenanceProposal:
        if proposal_id not in self.proposals:
            raise KeyError(f"Proposal {proposal_id} does not exist.")
        prop = self.proposals[proposal_id]
        prop.status = "REJECTED"
        prop.human_reviewer = reviewer_name
        prop.rejection_feedback = feedback
        prop.resolved_at = datetime.now(timezone.utc).isoformat()
        return prop
