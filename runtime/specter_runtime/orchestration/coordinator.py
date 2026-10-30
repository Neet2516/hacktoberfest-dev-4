import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional

from ..base import SpecterAgent
from ..context import AgentContext, AgentResult, AgentTaskState
from ..message_bus import AgentMessageBus
from ..agents.archaeologist import RepositoryArchaeologistAgent
from ..investigation.investigator import IssueInvestigatorAgent
from ..repair.repairer import GhostRepairerAgent
from ..review.reviewer import AdversarialReviewerAgent
from ..testing.tester import TestEngineerAgent
from .pipeline import PipelineExecution, WorkflowStep
from .approval import ApprovalGate, MaintenanceProposal

logger = logging.getLogger("specter.coordinator")

class ResurrectionCoordinatorAgent(SpecterAgent):
    """Orchestrates the autonomous 5-stage maintenance lifecycle from ingestion to human approval."""

    def __init__(
        self,
        agent_id: str = "coordinator",
        message_bus: Optional[AgentMessageBus] = None,
        approval_gate: Optional[ApprovalGate] = None,
    ):
        super().__init__(agent_id=agent_id, message_bus=message_bus)
        self.approval_gate = approval_gate or ApprovalGate()
        self.archaeologist = RepositoryArchaeologistAgent(message_bus=self.message_bus)
        self.investigator = IssueInvestigatorAgent(message_bus=self.message_bus)
        self.repairer = GhostRepairerAgent(message_bus=self.message_bus)
        self.reviewer = AdversarialReviewerAgent(message_bus=self.message_bus)
        self.tester = TestEngineerAgent(message_bus=self.message_bus)

    async def execute_resurrection_pipeline(
        self,
        pipeline_id: str,
        repository_url: str,
        workspace_path: str,
        issue_number: int,
        issue_title: str,
        issue_body: str,
    ) -> PipelineExecution:
        pipeline = PipelineExecution(
            pipeline_id=pipeline_id,
            repository_url=repository_url,
            workspace_path=workspace_path,
            issue_number=issue_number,
        )

        # ----------------------------------------------------
        # Step 1: Repository Archaeology
        # ----------------------------------------------------
        pipeline.current_step = WorkflowStep.ARCHAEOLOGY
        arch_ctx = AgentContext(
            task_id=f"{pipeline_id}_arch",
            repository_url=repository_url,
            workspace_path=workspace_path,
        )
        arch_res = await self.archaeologist.run(arch_ctx)
        pipeline.record_step(
            WorkflowStep.ARCHAEOLOGY,
            success=(arch_res.status == AgentTaskState.COMPLETED),
            summary=arch_res.summary,
            data=arch_res.data,
        )
        if arch_res.status != AgentTaskState.COMPLETED:
            pipeline.is_terminal = True
            pipeline.current_step = WorkflowStep.FAILED
            pipeline.failure_reason = "Archaeology stage failed."
            return pipeline

        # ----------------------------------------------------
        # Step 2: Issue Investigation
        # ----------------------------------------------------
        pipeline.current_step = WorkflowStep.INVESTIGATION
        inv_ctx = AgentContext(
            task_id=f"{pipeline_id}_inv",
            repository_url=repository_url,
            workspace_path=workspace_path,
            parameters={
                "issue_number": issue_number,
                "issue_title": issue_title,
                "issue_body": issue_body,
                "context_report": arch_res.data,
            },
        )
        inv_res = await self.investigator.run(inv_ctx)
        pipeline.record_step(
            WorkflowStep.INVESTIGATION,
            success=(inv_res.status == AgentTaskState.COMPLETED),
            summary=inv_res.summary,
            data=inv_res.data,
        )
        if inv_res.status != AgentTaskState.COMPLETED:
            pipeline.is_terminal = True
            pipeline.current_step = WorkflowStep.FAILED
            pipeline.failure_reason = "Issue investigation stage failed."
            return pipeline

        repair_spec = inv_res.data.get("repair_spec", {})

        # ----------------------------------------------------
        # Step 3, 4, 5: Repair, Review, and Test Execution with Retries
        # ----------------------------------------------------
        while pipeline.repair_attempts < pipeline.max_repair_attempts:
            pipeline.repair_attempts += 1
            pipeline.current_step = WorkflowStep.REPAIR

            # 3. Code Repair
            repair_ctx = AgentContext(
                task_id=f"{pipeline_id}_rep_{pipeline.repair_attempts}",
                repository_url=repository_url,
                workspace_path=workspace_path,
                parameters={"repair_spec": repair_spec},
            )
            repair_res = await self.repairer.run(repair_ctx)
            pipeline.record_step(
                WorkflowStep.REPAIR,
                success=(repair_res.status == AgentTaskState.COMPLETED),
                summary=repair_res.summary,
                data=repair_res.data,
            )
            if repair_res.status != AgentTaskState.COMPLETED:
                continue

            patch_diff = repair_res.data.get("patch_diff", "")
            target_file = repair_spec.get("target_file", "src/lib.rs")

            # 4. Adversarial Review
            pipeline.current_step = WorkflowStep.REVIEW
            rev_ctx = AgentContext(
                task_id=f"{pipeline_id}_rev_{pipeline.repair_attempts}",
                repository_url=repository_url,
                workspace_path=workspace_path,
                parameters={
                    "diff_content": patch_diff,
                    "target_file": target_file,
                },
            )
            rev_res = await self.reviewer.run(rev_ctx)
            pipeline.record_step(
                WorkflowStep.REVIEW,
                success=(rev_res.status == AgentTaskState.COMPLETED and rev_res.data.get("approved", False)),
                summary=rev_res.summary,
                data=rev_res.data,
            )

            if not rev_res.data.get("approved", False):
                logger.warning(f"Review rejected patch in attempt {pipeline.repair_attempts}. Looping back to repair.")
                continue

            # 5. Isolated Test Execution
            pipeline.current_step = WorkflowStep.TESTING
            test_ctx = AgentContext(
                task_id=f"{pipeline_id}_test_{pipeline.repair_attempts}",
                repository_url=repository_url,
                workspace_path=workspace_path,
            )
            test_res = await self.tester.run(test_ctx)
            pipeline.record_step(
                WorkflowStep.TESTING,
                success=(test_res.status == AgentTaskState.COMPLETED and test_res.data.get("verified", False)),
                summary=test_res.summary,
                data=test_res.data,
            )

            if test_res.data.get("verified", False):
                # ----------------------------------------------------
                # Step 6: Create Proposal & Await Human Approval Gate
                # ----------------------------------------------------
                pipeline.current_step = WorkflowStep.PENDING_APPROVAL
                proposal = self.approval_gate.create_proposal(
                    pipeline_id=pipeline_id,
                    repository_url=repository_url,
                    issue_number=issue_number,
                    issue_title=issue_title,
                    patch_diff=patch_diff,
                    files_changed=[target_file],
                    verification_summary=test_res.summary,
                    review_verdict=rev_res.data.get("verdict", "APPROVED"),
                    risk_level=rev_res.data.get("regression_risk", "LOW"),
                )
                pipeline.record_step(
                    WorkflowStep.PENDING_APPROVAL,
                    success=True,
                    summary=f"Proposal {proposal.proposal_id} ready for human signoff.",
                    data={"proposal": proposal.__dict__},
                )
                return pipeline

        # If loops exhausted
        pipeline.current_step = WorkflowStep.FAILED
        pipeline.is_terminal = True
        pipeline.failure_reason = f"Max repair attempts ({pipeline.max_repair_attempts}) reached without passing verification."
        return pipeline

    async def run(self, context: AgentContext) -> AgentResult:
        """Standard Agent interface for Coordinator execution."""
        pipeline_id = context.task_id
        issue_number = context.parameters.get("issue_number", 1)
        issue_title = context.parameters.get("issue_title", "Defect")
        issue_body = context.parameters.get("issue_body", "Details")

        pipeline = await self.execute_resurrection_pipeline(
            pipeline_id=pipeline_id,
            repository_url=context.repository_url,
            workspace_path=context.workspace_path,
            issue_number=issue_number,
            issue_title=issue_title,
            issue_body=issue_body,
        )

        return AgentResult(
            agent_id=self.agent_id,
            task_id=pipeline_id,
            status=AgentTaskState.COMPLETED if pipeline.current_step == WorkflowStep.PENDING_APPROVAL else AgentTaskState.FAILED,
            output_type="resurrection_pipeline_result",
            summary=f"Resurrection pipeline ended in step: {pipeline.current_step.value}",
            data={
                "current_step": pipeline.current_step.value,
                "repair_attempts": pipeline.repair_attempts,
                "failure_reason": pipeline.failure_reason,
            },
        )

