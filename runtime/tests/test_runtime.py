import unittest
import asyncio
import sys
import os

# Add runtime directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from specter_runtime import (
    AgentContext,
    AgentResult,
    AgentTaskState,
    SpecterAgent,
    AgentMessageBus,
    AgentMessage,
)

class MockArchaeologistAgent(SpecterAgent):
    async def run(self, context: AgentContext) -> AgentResult:
        await self.emit_message(
            to="resurrection_coordinator",
            task_id=context.task_id,
            message_type="repository_context",
            payload={"languages": ["Rust", "Python"], "ast_valid": True},
            status="completed",
        )
        return AgentResult(
            agent_id=self.agent_id,
            task_id=context.task_id,
            status=AgentTaskState.COMPLETED,
            output_type="context_report",
            summary="Extracted repository AST and languages",
            data={"languages": ["Rust", "Python"]},
            evidence_refs=["git:commit:head"],
        )

class TestSpecterRuntime(unittest.TestCase):
    def test_agent_context_instantiation(self):
        ctx = AgentContext(
            task_id="SPECTER-002",
            repository_url="https://github.com/example/repo",
            workspace_path="/tmp/test_ws",
        )
        self.assertEqual(ctx.task_id, "SPECTER-002")
        self.assertEqual(ctx.repository_url, "https://github.com/example/repo")

    def test_message_bus_delivery(self):
        bus = AgentMessageBus()
        received = []

        bus.subscribe("resurrection_coordinator", lambda msg: received.append(msg))

        msg = AgentMessage(
            message_id="msg_0123456789abcdef",
            from_agent="repository_archaeologist",
            to_agent="resurrection_coordinator",
            task_id="SPECTER-002",
            message_type="acknowledgment",
            payload={"ack": True},
        )
        bus.publish(msg)

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].message_id, "msg_0123456789abcdef")
        self.assertEqual(received[0].to_agent, "resurrection_coordinator")

    def test_agent_lifecycle_and_emission(self):
        bus = AgentMessageBus()
        agent = MockArchaeologistAgent(agent_id="repository_archaeologist", message_bus=bus)

        ctx = AgentContext(
            task_id="SPECTER-002",
            repository_url="https://github.com/example/repo",
            workspace_path="/tmp/test_ws",
        )

        result = asyncio.run(agent.run(ctx))
        self.assertEqual(result.status, AgentTaskState.COMPLETED)
        self.assertEqual(result.agent_id, "repository_archaeologist")
        
        messages = bus.get_task_messages("SPECTER-002")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message_type, "repository_context")

if __name__ == "__main__":
    unittest.main()
