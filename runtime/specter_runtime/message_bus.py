import json
import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class MessageAcknowledgment:
    ack_id: str
    message_id: str
    recipient: str
    status: str  # "delivered", "processed", "rejected"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

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

class MessageValidator:
    REQUIRED_FIELDS = ["message_id", "from", "to", "task_id", "message_type", "payload", "timestamp"]

    @classmethod
    def validate(cls, msg_dict: Dict[str, Any]) -> bool:
        for field in cls.REQUIRED_FIELDS:
            if field not in msg_dict:
                raise ValueError(f"Message validation error: missing required field '{field}'.")
        if not re.match(r"^msg_[a-zA-Z0-9_-]+$", msg_dict["message_id"]):
            raise ValueError(f"Invalid message_id format: {msg_dict['message_id']}")
        return True

class AgentMessageBus:
    def __init__(self):
        self._history: List[AgentMessage] = []
        self._subscribers: Dict[str, List[Any]] = {}
        self._acknowledgments: List[MessageAcknowledgment] = []

    def publish(self, message: AgentMessage) -> MessageAcknowledgment:
        MessageValidator.validate(message.to_dict())
        self._history.append(message)
        
        delivered = False
        if message.to_agent in self._subscribers:
            for cb in self._subscribers[message.to_agent]:
                cb(message)
            delivered = True
                
        if "broadcast" in self._subscribers:
            for cb in self._subscribers["broadcast"]:
                cb(message)
            delivered = True
                
        ack = MessageAcknowledgment(
            ack_id=f"ack_{len(self._acknowledgments)+1:04d}",
            message_id=message.message_id,
            recipient=message.to_agent,
            status="delivered" if delivered else "enqueued",
        )
        self._acknowledgments.append(ack)
        return ack

    def subscribe(self, agent_id: str, callback: Any) -> None:
        if agent_id not in self._subscribers:
            self._subscribers[agent_id] = []
        self._subscribers[agent_id].append(callback)

    def get_task_messages(self, task_id: str) -> List[AgentMessage]:
        return [m for m in self._history if m.task_id == task_id]

    def get_acknowledgments(self, message_id: str) -> List[MessageAcknowledgment]:
        return [a for a in self._acknowledgments if a.message_id == message_id]
