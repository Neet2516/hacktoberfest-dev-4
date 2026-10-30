import json
import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class AgentMessage:
    message_id: str
    from_agent: str
    to_agent: str
    task_id: str
    message_type: str
    payload: Dict[str, Any]
    evidence_refs: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    execution_status: str = "pending"
    schema_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "from": self.from_agent,
            "to": self.to_agent,
            "task_id": self.task_id,
            "message_type": self.message_type,
            "payload": self.payload,
            "evidence_refs": self.evidence_refs,
            "timestamp": self.timestamp,
            "execution_status": self.execution_status,
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        return cls(
            message_id=data["message_id"],
            from_agent=data.get("from") or data["from_agent"],
            to_agent=data.get("to") or data["to_agent"],
            task_id=data["task_id"],
            message_type=data["message_type"],
            payload=data.get("payload", {}),
            evidence_refs=data.get("evidence_refs", []),
            timestamp=data.get("timestamp") or datetime.now(timezone.utc).isoformat(),
            execution_status=data.get("execution_status", "pending"),
            schema_version=data.get("schema_version", "1.0.0"),
        )

class AgentMessageBus:
    def __init__(self):
        self._history: List[AgentMessage] = []
        self._subscribers: Dict[str, List[Any]] = {}

    def publish(self, message: AgentMessage) -> bool:
        if not re.match(r"^msg_[a-zA-Z0-9_-]+$", message.message_id):
            raise ValueError(f"Invalid message_id format: {message.message_id}")
        
        self._history.append(message)
        
        if message.to_agent in self._subscribers:
            for cb in self._subscribers[message.to_agent]:
                cb(message)
                
        if "broadcast" in self._subscribers:
            for cb in self._subscribers["broadcast"]:
                cb(message)
                
        return True

    def subscribe(self, agent_id: str, callback: Any) -> None:
        if agent_id not in self._subscribers:
            self._subscribers[agent_id] = []
        self._subscribers[agent_id].append(callback)

    def get_task_messages(self, task_id: str) -> List[AgentMessage]:
        return [m for m in self._history if m.task_id == task_id]
