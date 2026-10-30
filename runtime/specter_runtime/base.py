from abc import ABC, abstractmethod
import uuid
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone

from .context import AgentContext, AgentResult, AgentTaskState
from .message_bus import AgentMessageBus, AgentMessage

class SpecterAgent(ABC):
    """Abstract base class for all SPECTER specialized AI agents."""

    def __init__(
        self,
        agent_id: str,
        message_bus: Optional[AgentMessageBus] = None,
    ):
        self.agent_id = agent_id
        self.message_bus = message_bus or AgentMessageBus()

    @abstractmethod
    async def run(self, context: AgentContext) -> AgentResult:
        """Execute the agent's core responsibility on the given context."""
        pass

    async def emit_message(
        self,
        to: str,
        task_id: str,
        message_type: str,
        payload: Dict[str, Any],
        status: str = "in_progress",
        evidence_refs: Optional[List[str]] = None,
    ) -> AgentMessage:
        """Construct and publish a verified A2A message to the message bus."""
        msg_id = f"msg_{uuid.uuid4().hex}"
        msg = AgentMessage(
            message_id=msg_id,
            from_agent=self.agent_id,
            to_agent=to,
            task_id=task_id,
            message_type=message_type,
            payload=payload,
            evidence_refs=evidence_refs or [],
            timestamp=datetime.now(timezone.utc).isoformat(),
            execution_status=status,
            schema_version="1.0.0",
        )
        self.message_bus.publish(msg)
        return msg
