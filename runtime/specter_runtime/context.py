from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

class AgentTaskState(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"
    BLOCKED = "blocked"

@dataclass
class AgentContext:
    task_id: str
    repository_url: str
    workspace_path: str
    baseline_commit: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentResult:
    agent_id: str
    task_id: str
    status: AgentTaskState
    output_type: str
    summary: str
    data: Dict[str, Any] = field(default_factory=dict)
    evidence_refs: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
