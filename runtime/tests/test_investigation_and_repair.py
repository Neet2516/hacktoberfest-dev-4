import unittest
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from specter_runtime.investigation.investigator import IssueInvestigatorAgent, RepairSpecification
from specter_runtime.repair.repairer import GhostRepairerAgent, ProposedPatch
from specter_runtime.context import AgentContext, AgentTaskState
from specter_runtime.message_bus import AgentMessageBus
from specter_runtime.llm.client import OllamaClient

class TestInvestigationAndRepair(unittest.TestCase):
    def test_investigator_generates_spec(self):
        bus = AgentMessageBus()
        client = OllamaClient(mock_mode=True)
        investigator = IssueInvestigatorAgent(message_bus=bus, ollama_client=client)

        ctx = AgentContext(
            task_id="SPECTER-062",
            repository_url="https://github.com/example/repo",
            workspace_path="/tmp/test_ws",
            parameters={
                "issue_number": 42,
                "issue_title": "Panic on empty slice",
                "target_file": "src/parser.rs",
            },
        )

        result = asyncio.run(investigator.run(ctx))
        self.assertEqual(result.status, AgentTaskState.COMPLETED)
        self.assertEqual(result.output_type, "investigation_report")

        messages = bus.get_task_messages("SPECTER-062")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].to_agent, "ghost_repairer")
        self.assertEqual(messages[0].message_type, "repair_specification")
        self.assertIn("affected_files", messages[0].payload)

    def test_repairer_generates_minimal_patch(self):
        bus = AgentMessageBus()
        client = OllamaClient(mock_mode=True)
        repairer = GhostRepairerAgent(message_bus=bus, ollama_client=client)

        ctx = AgentContext(
            task_id="SPECTER-068",
            repository_url="https://github.com/example/repo",
            workspace_path="/tmp/test_ws",
            parameters={
                "repair_specification": {
                    "problem_statement": "Panic on empty slice",
                    "affected_files": [{"file_path": "src/parser.rs"}],
                    "root_cause": "No length check",
                }
            },
        )

        result = asyncio.run(repairer.run(ctx))
        self.assertEqual(result.status, AgentTaskState.COMPLETED)
        self.assertEqual(result.output_type, "git_patch")

        messages = bus.get_task_messages("SPECTER-068")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].to_agent, "adversarial_reviewer")
        self.assertEqual(messages[0].message_type, "patch_proposal")
        self.assertTrue(messages[0].payload["diff_content"].startswith("diff --git"))

if __name__ == "__main__":
    unittest.main()

