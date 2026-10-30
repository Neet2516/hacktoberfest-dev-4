import unittest
import asyncio
import tempfile
import os
from specter_runtime.context import AgentContext
from specter_runtime.message_bus import AgentMessageBus
from specter_runtime.orchestration.approval import ApprovalGate, MaintenanceProposal
from specter_runtime.orchestration.coordinator import ResurrectionCoordinatorAgent, WorkflowStep

class TestCoordinatorAndApproval(unittest.TestCase):
    def test_approval_gate_lifecycle(self):
        gate = ApprovalGate()
        prop = gate.create_proposal(
            pipeline_id="pipe_101",
            repository_url="https://github.com/org/repo",
            issue_number=42,
            issue_title="Fix memory leak",
            patch_diff="--- a/lib.rs\n+++ b/lib.rs\n@@ -1 +1 @@\n-leak();\n+drop();",
            files_changed=["lib.rs"],
            verification_summary="5 passed, 0 failed",
            review_verdict="APPROVED",
        )
        self.assertEqual(prop.status, "PENDING_APPROVAL")
        self.assertIn("pipe_101", gate.proposals[prop.proposal_id].pipeline_id)

        # PR formatting check
        pr_payload = prop.format_github_pr()
        self.assertIn("Fix #42: Fix memory leak", pr_payload["title"])
        self.assertIn("SPECTER Autonomous Maintenance Proposal", pr_payload["body"])
        self.assertIn("diff", pr_payload["body"])

        # Approve
        approved = gate.approve(prop.proposal_id, reviewer_name="alice_maintainer")
        self.assertEqual(approved.status, "APPROVED")
        self.assertEqual(approved.human_reviewer, "alice_maintainer")
        self.assertIsNotNone(approved.resolved_at)

        # Reject
        prop2 = gate.create_proposal(
            pipeline_id="pipe_102",
            repository_url="https://github.com/org/repo",
            issue_number=43,
            issue_title="Flaky timeout",
            patch_diff="",
            files_changed=[],
            verification_summary="",
            review_verdict="REQUEST_CHANGES",
        )
        rejected = gate.reject(prop2.proposal_id, reviewer_name="bob_maintainer", feedback="Requires deeper fix.")
        self.assertEqual(rejected.status, "REJECTED")
        self.assertEqual(rejected.rejection_feedback, "Requires deeper fix.")

    def test_resurrection_coordinator_pipeline_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Set up mock repository workspace
            with open(os.path.join(tmp_dir, "Cargo.toml"), "w") as f:
                f.write("[package]\nname = 'mock_abandoned'\nversion = '0.1.0'\n")
            src_dir = os.path.join(tmp_dir, "src")
            os.makedirs(src_dir, exist_ok=True)
            with open(os.path.join(src_dir, "lib.rs"), "w") as f:
                f.write("pub fn broken() { panic!(); }\n")
            with open(os.path.join(tmp_dir, "README.md"), "w") as f:
                f.write("# Mock Repository\nMaintained until 2021.")

            coordinator = ResurrectionCoordinatorAgent()
            pipeline = asyncio.run(coordinator.execute_resurrection_pipeline(
                pipeline_id="pipe_test_200",
                repository_url="https://github.com/mock/repo",
                workspace_path=tmp_dir,
                issue_number=1,
                issue_title="Panic in broken() function",
                issue_body="Calling broken() causes panic on startup in src/lib.rs",
            ))

            self.assertEqual(pipeline.current_step, WorkflowStep.PENDING_APPROVAL)
            self.assertIn(WorkflowStep.ARCHAEOLOGY.value, pipeline.step_results)
            self.assertIn(WorkflowStep.INVESTIGATION.value, pipeline.step_results)
            self.assertIn(WorkflowStep.REPAIR.value, pipeline.step_results)
            self.assertIn(WorkflowStep.REVIEW.value, pipeline.step_results)
            self.assertIn(WorkflowStep.TESTING.value, pipeline.step_results)
            self.assertIn(WorkflowStep.PENDING_APPROVAL.value, pipeline.step_results)

if __name__ == "__main__":
    unittest.main()
