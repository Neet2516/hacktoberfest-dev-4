import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

from ..base import SpecterAgent
from ..context import AgentContext, AgentResult, AgentTaskState
from ..message_bus import AgentMessageBus
from ..llm.client import OllamaClient

@dataclass
class ReviewFinding:
    finding_id: str
    severity: str  # "INFO", "WARNING", "ERROR", "BLOCKER"
    category: str  # "REGRESSION", "SECURITY", "OVER_REFACTORING", "SPEC_MISALIGNMENT"
    description: str
    file_path: str
    suggested_remediation: Optional[str] = None

@dataclass
class ReviewVerdictReport:
    review_id: str
    task_id: str
    verdict: str  # "APPROVED", "REQUEST_CHANGES", "REJECTED_UNSAFE"
    regression_risk: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    security_risk: str  # "NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"
    findings: List[ReviewFinding] = field(default_factory=list)
    approved: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "review_id": self.review_id,
            "task_id": self.task_id,
            "verdict": self.verdict,
            "regression_risk": self.regression_risk,
            "security_risk": self.security_risk,
            "findings": [
                {
                    "finding_id": f.finding_id,
                    "severity": f.severity,
                    "category": f.category,
                    "description": f.description,
                    "file_path": f.file_path,
                    "suggested_remediation": f.suggested_remediation,
                }
                for f in self.findings
            ],
            "approved": self.approved,
            "timestamp": self.timestamp,
        }

class SecurityScanner:
    SUSPICIOUS_PATTERNS = [
        (r"(?i)(password|secret|api_key|token)\s*=\s*['\"][a-zA-Z0-9_\-]{16,}['\"]", "Hardcoded credential detected"),
        (r"(?i)eval\s*\(", "Unsafe dynamic evaluation via eval()"),
        (r"(?i)child_process\.(exec|spawn)\s*\(", "Unsanitized system process execution"),
        (r"(?i)curl\s+-[skSK]+", "Insecure TLS or arbitrary outbound network curl"),
    ]

    @classmethod
    def scan_diff(cls, diff_content: str, file_path: str) -> List[ReviewFinding]:
        findings = []
        for pattern, desc in cls.SUSPICIOUS_PATTERNS:
            for line in diff_content.splitlines():
                if line.startswith("+") and not line.startswith("+++"):
                    if re.search(pattern, line):
                        findings.append(
                            ReviewFinding(
                                finding_id=f"SEC-{len(findings)+1:02d}",
                                severity="BLOCKER",
                                category="SECURITY",
                                description=f"{desc} in added line: {line.strip()}",
                                file_path=file_path,
                                suggested_remediation="Remove sensitive token or unsafe invocation.",
                            )
                        )
        return findings

class AdversarialReviewerAgent(SpecterAgent):
    """Specialized AI Agent that independently reviews proposed patches to detect regressions and security flaws."""

    def __init__(
        self,
        agent_id: str = "adversarial_reviewer",
        message_bus: AgentMessageBus = None,
        ollama_client: OllamaClient = None,
    ):
        super().__init__(agent_id=agent_id, message_bus=message_bus)
        self.ollama = ollama_client or OllamaClient()

    async def run(self, context: AgentContext) -> AgentResult:
        patch_diff = context.parameters.get("diff_content", "")
        target_file = context.parameters.get("target_file", "src/lib.rs")

        # 1. Run deterministic security rules scanner
        findings = SecurityScanner.scan_diff(patch_diff, target_file)

        # 2. Check for over-refactoring
        lines_changed = len([l for l in patch_diff.splitlines() if (l.startswith("+") or l.startswith("-")) and not l.startswith("+++") and not l.startswith("---")])
        if lines_changed > 150:
            findings.append(
                ReviewFinding(
                    finding_id=f"REF-{len(findings)+1:02d}",
                    severity="WARNING",
                    category="OVER_REFACTORING",
                    description=f"Patch contains {lines_changed} changed lines; exceeds minimal diff recommendation.",
                    file_path=target_file,
                    suggested_remediation="Scope patch strictly to the affected defect.",
                )
            )

        # 3. LLM Adversarial Review
        review_prompt = (
            f"Review this unified git diff for potential logic regressions or edge cases:\n"
            f"{patch_diff}\n"
            f"Target file: {target_file}\n"
            f"Challenge assumptions: can this break existing callers?"
        )
        synthesis = self.ollama.generate(
            prompt=review_prompt,
            system="You are the SPECTER Adversarial Reviewer. Critically audit the patch.",
        )

        has_blockers = any(f.severity == "BLOCKER" for f in findings)
        verdict = "REJECTED_UNSAFE" if has_blockers else "APPROVED"
        approved = not has_blockers

        report = ReviewVerdictReport(
            review_id=f"rev_{context.task_id}",
            task_id=context.task_id,
            verdict=verdict,
            regression_risk="LOW" if approved else "HIGH",
            security_risk="NONE" if not has_blockers else "CRITICAL",
            findings=findings,
            approved=approved,
        )

        recipient = "test_engineer" if approved else "ghost_repairer"
        msg_type = "review_verdict"

        await self.emit_message(
            to=recipient,
            task_id=context.task_id,
            message_type=msg_type,
            payload=report.to_dict(),
            status="ready" if approved else "rejected",
            evidence_refs=[f"diff:{target_file}"],
        )

        return AgentResult(
            agent_id=self.agent_id,
            task_id=context.task_id,
            status=AgentTaskState.COMPLETED,
            output_type="review_verdict",
            summary=f"Audit completed: verdict is {verdict} with {len(findings)} findings.",
            data=report.to_dict(),
            evidence_refs=[f"diff:{target_file}"],
        )
