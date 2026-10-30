import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from ..base import SpecterAgent
from ..context import AgentContext, AgentResult, AgentTaskState
from ..message_bus import AgentMessageBus
from .framework_detector import TestFrameworkDetector
from .sandbox_runner import DockerTestSandbox
from .output_parser import TestOutputParser, TestSummary

@dataclass
class VerificationReport:
    report_id: str
    task_id: str
    framework: str
    test_summary: TestSummary
    verified: bool
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "task_id": self.task_id,
            "framework": self.framework,
            "verified": self.verified,
            "total_tests": self.test_summary.total,
            "passed_tests": self.test_summary.passed,
            "failed_tests": self.test_summary.failed,
            "failure_messages": self.test_summary.failure_messages,
            "timestamp": self.timestamp,
            "details": self.details,
        }

class TestEngineerAgent(SpecterAgent):
    """Specialized AI Agent that discovers test suites, runs them in an isolated sandbox, and produces verification reports."""

    def __init__(
        self,
        agent_id: str = "test_engineer",
        message_bus: Optional[AgentMessageBus] = None,
        sandbox: Optional[DockerTestSandbox] = None,
    ):
        super().__init__(agent_id=agent_id, message_bus=message_bus)
        self.sandbox = sandbox or DockerTestSandbox()

    async def run(self, context: AgentContext) -> AgentResult:
        # 1. Detect framework in workspace
        fw_config = TestFrameworkDetector.detect(context.workspace_path)

        # 2. Execute test command in Docker sandbox
        custom_cmd = context.parameters.get("test_command")
        run_cmd = custom_cmd if custom_cmd else fw_config.command

        execution = self.sandbox.execute(context.workspace_path, run_cmd)

        # 3. Parse test output
        summary = TestOutputParser.parse(
            framework=fw_config.framework_name,
            stdout=execution.stdout,
            stderr=execution.stderr,
            exit_code=execution.exit_code,
        )

        verified = summary.success and (execution.exit_code == 0)

        report = VerificationReport(
            report_id=f"verif_{context.task_id}",
            task_id=context.task_id,
            framework=fw_config.framework_name,
            test_summary=summary,
            verified=verified,
            details={
                "exit_code": execution.exit_code,
                "timed_out": execution.timed_out,
                "command": run_cmd,
            },
        )

        # 4. Emit message to coordinator
        await self.emit_message(
            to="coordinator",
            task_id=context.task_id,
            message_type="verification_report",
            payload=report.to_dict(),
            status="verified" if verified else "failed",
            evidence_refs=[f"workspace:{context.workspace_path}"],
        )

        return AgentResult(
            agent_id=self.agent_id,
            task_id=context.task_id,
            status=AgentTaskState.COMPLETED if verified else AgentTaskState.FAILED,
            output_type="verification_report",
            summary=f"Test verification {'succeeded' if verified else 'failed'}: {summary.passed}/{summary.total} passed.",
            data=report.to_dict(),
            evidence_refs=[f"workspace:{context.workspace_path}"],
        )
