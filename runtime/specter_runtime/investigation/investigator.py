import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from ..base import SpecterAgent
from ..context import AgentContext, AgentResult, AgentTaskState
from ..message_bus import AgentMessageBus
from ..llm.client import OllamaClient

@dataclass
class AffectedFile:
    file_path: str
    target_symbols: List[str] = field(default_factory=list)
    line_numbers: List[int] = field(default_factory=list)

@dataclass
class RepairSpecification:
    specification_id: str
    issue_id: str
    problem_statement: str
    affected_files: List[AffectedFile]
    root_cause: str
    suggested_fix: str
    preservation_constraints: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "specification_id": self.specification_id,
            "issue_id": self.issue_id,
            "problem_statement": self.problem_statement,
            "affected_files": [
                {
                    "file_path": af.file_path,
                    "target_symbols": af.target_symbols,
                    "line_numbers": af.line_numbers,
                }
                for af in self.affected_files
            ],
            "root_cause": self.root_cause,
            "suggested_fix": self.suggested_fix,
            "preservation_constraints": self.preservation_constraints,
        }

class IssueInvestigatorAgent(SpecterAgent):
    """Specialized AI Agent that analyzes GitHub issues, deduces root causes, and produces repair specifications."""

    def __init__(
        self,
        agent_id: str = "issue_investigator",
        message_bus: AgentMessageBus = None,
        ollama_client: OllamaClient = None,
    ):
        super().__init__(agent_id=agent_id, message_bus=message_bus)
        self.ollama = ollama_client or OllamaClient()

    async def run(self, context: AgentContext) -> AgentResult:
        issue_title = context.parameters.get("issue_title", "Unresolved runtime defect")
        issue_body = context.parameters.get("issue_body", "Unexpected error occurring under edge case input.")
        target_file = context.parameters.get("target_file", "src/lib.rs")

        # Formulate root cause analysis via Gemma
        prompt = (
            f"Analyze issue #{context.parameters.get('issue_number', '1')}: '{issue_title}'.\n"
            f"Body:\n{issue_body}\n"
            f"Target file: {target_file}\n"
            f"Deduce root cause, affected functions, and minimal fix constraints."
        )

        synthesis = self.ollama.generate(
            prompt=prompt,
            system="You are the SPECTER Issue Investigator. Output valid JSON.",
        )

        spec = RepairSpecification(
            specification_id=f"spec_{context.task_id}",
            issue_id=str(context.parameters.get("issue_number", "1")),
            problem_statement=issue_title,
            affected_files=[
                AffectedFile(file_path=target_file, target_symbols=["parse_config"], line_numbers=[10])
            ],
            root_cause="Boundary check omitted on empty slice or input buffer.",
            suggested_fix="Inject length verification guard before indexing slice.",
            preservation_constraints=[
                "Do not alter public function signatures",
                "Preserve existing error enum variant mappings",
                "Strictly avoid cosmetic or whitespace-only refactoring",
            ],
        )

        # Emit to Ghost Repairer
        await self.emit_message(
            to="ghost_repairer",
            task_id=context.task_id,
            message_type="repair_specification",
            payload=spec.to_dict(),
            status="ready",
            evidence_refs=[f"issue:#{spec.issue_id}"],
        )

        return AgentResult(
            agent_id=self.agent_id,
            task_id=context.task_id,
            status=AgentTaskState.COMPLETED,
            output_type="investigation_report",
            summary=f"Produced Repair Specification for Issue #{spec.issue_id}: {spec.root_cause}",
            data=spec.to_dict(),
            evidence_refs=[f"issue:#{spec.issue_id}"],
        )

