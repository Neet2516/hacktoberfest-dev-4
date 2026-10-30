from abc import ABC, abstractmethod
import asyncio
import time
import uuid
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone

from .context import AgentContext, AgentResult, AgentTaskState
from .message_bus import AgentMessageBus, AgentMessage

class AgentTimeoutError(TimeoutError):
    pass

class SpecterAgent(ABC):
    """Abstract base class for all SPECTER specialized AI agents."""

    def __init__(
        self,
        agent_id: str,
        message_bus: Optional[AgentMessageBus] = None,
        default_timeout_seconds: float = 60.0,
    ):
        self.agent_id = agent_id
        self.message_bus = message_bus or AgentMessageBus()
        self.default_timeout_seconds = default_timeout_seconds

    @abstractmethod
    async def run(self, context: AgentContext) -> AgentResult:
        """Execute the agent's core responsibility on the given context."""
        pass

    async def execute_with_timeout(
        self, context: AgentContext, timeout_seconds: Optional[float] = None
    ) -> AgentResult:
        """Executes agent task with strict asynchronous timeout enforcement and performance monitoring."""
        limit = timeout_seconds or self.default_timeout_seconds
        start_time = time.perf_counter()
        try:
            result = await asyncio.wait_for(self.run(context), timeout=limit)
            duration = time.perf_counter() - start_time
            result.metadata = result.metadata if hasattr(result, "metadata") else {}
            return result
        except asyncio.TimeoutError as exc:
            duration = time.perf_counter() - start_time
            raise AgentTimeoutError(
                f"Agent '{self.agent_id}' execution timed out after {duration:.2f}s (limit: {limit}s)."
            ) from exc

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
