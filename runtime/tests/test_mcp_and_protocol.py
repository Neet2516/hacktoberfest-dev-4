import unittest
import asyncio
from specter_runtime.mcp_host import MCPToolHost, ToolAccessDeniedError
from specter_runtime.message_bus import AgentMessageBus, AgentMessage, MessageValidator
from specter_runtime.base import SpecterAgent, AgentTimeoutError
from specter_runtime.context import AgentContext, AgentResult, AgentTaskState

class SlowAgent(SpecterAgent):
    async def run(self, context: AgentContext) -> AgentResult:
        await asyncio.sleep(0.5)
        return AgentResult(
            agent_id=self.agent_id,
            task_id=context.task_id,
            status=AgentTaskState.COMPLETED,
            output_type="slow_result",
            summary="Completed slowly",
        )

class TestMCPAndProtocolSubsystem(unittest.TestCase):
    def test_mcp_least_privilege_enforcement(self):
        host = MCPToolHost()
        
        # Test Archaeologist permissions
        self.assertTrue(host.can_agent_use_tool("repository_archaeologist", "read_file"))
        self.assertFalse(host.can_agent_use_tool("repository_archaeologist", "execute_sandbox_test"))

        # Test unauthorized invocation raises error
        with self.assertRaises(ToolAccessDeniedError):
            host.invoke("repository_archaeologist", "execute_sandbox_test")

        # Test authorized invocation
        res = host.invoke("repository_archaeologist", "read_file", path="README.md")
        self.assertEqual(res["status"], "success")

    def test_message_validation_and_acknowledgment(self):
        bus = AgentMessageBus()
        delivered_msgs = []

        bus.subscribe("ghost_repairer", lambda m: delivered_msgs.append(m))

        msg = AgentMessage(
            message_id="msg_test_001",
            from_agent="issue_investigator",
            to_agent="ghost_repairer",
            task_id="task_123",
            message_type="repair_spec",
            payload={"defect": "nil pointer"},
        )

        ack = bus.publish(msg)
        self.assertEqual(ack.status, "delivered")
        self.assertEqual(ack.message_id, "msg_test_001")
        self.assertEqual(len(delivered_msgs), 1)

    def test_message_validation_invalid_id(self):
        with self.assertRaises(ValueError):
            MessageValidator.validate({
                "message_id": "invalid!id#",
                "from": "a",
                "to": "b",
                "task_id": "t",
                "message_type": "m",
                "payload": {},
                "timestamp": "2026-10-31T00:00:00Z"
            })

    def test_agent_execution_timeout(self):
        agent = SlowAgent(agent_id="slow_agent")
        ctx = AgentContext(
            task_id="timeout_test",
            repository_url="https://github.com/test",
            workspace_path="/tmp",
        )

        with self.assertRaises(AgentTimeoutError):
            asyncio.run(agent.execute_with_timeout(ctx, timeout_seconds=0.1))

if __name__ == "__main__":
    unittest.main()
