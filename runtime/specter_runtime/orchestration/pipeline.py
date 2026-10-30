from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

class WorkflowStep(str, Enum):
    INITIALIZED = "initialized"
    ARCHAEOLOGY = "archaeology"
    INVESTIGATION = "investigation"
    REPAIR = "repair"
    REVIEW = "review"
    TESTING = "testing"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class PipelineStepResult:
    step: WorkflowStep
    success: bool
    summary: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class PipelineExecution:
    pipeline_id: str
    repository_url: str
    workspace_path: str
    issue_number: int
    current_step: WorkflowStep = WorkflowStep.INITIALIZED
    repair_attempts: int = 0
    max_repair_attempts: int = 3
    step_results: Dict[str, PipelineStepResult] = field(default_factory=dict)
    is_terminal: bool = False
    failure_reason: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def record_step(self, step: WorkflowStep, success: bool, summary: str, data: Dict[str, Any]):
        self.step_results[step.value] = PipelineStepResult(
            step=step,
            success=success,
            summary=summary,
            data=data,
        )
        self.current_step = step
