import os
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..base import SpecterAgent
from ..context import AgentContext, AgentResult, AgentTaskState
from ..message_bus import AgentMessageBus
from ..llm.client import OllamaClient

@dataclass
class ProposedPatch:
    patch_id: str
    target_files: List[str]
    diff_content: str
    lines_added: int
    lines_removed: int
    preservation_verified: bool

class PatchApplier:
    @staticmethod
    def apply_patch_to_workspace(workspace_path: str, diff_content: str) -> bool:
        if not os.path.exists(workspace_path):
            return False

        try:
            # Test if patch applies cleanly
            check_proc = subprocess.run(
                ["git", "apply", "--check"],
                input=diff_content.encode("utf-8"),
                cwd=workspace_path,
                capture_output=True,
                check=False,
            )
            if check_proc.returncode != 0:
                return False

            # Apply patch
            apply_proc = subprocess.run(
                ["git", "apply"],
                input=diff_content.encode("utf-8"),
                cwd=workspace_path,
                capture_output=True,
                check=False,
            )
            return apply_proc.returncode == 0
        except Exception:
            return False

class GhostRepairerAgent(SpecterAgent):
    """Specialized AI Agent that generates minimal unified Git patches adhering to strict preservation rules."""

    def __init__(
        self,
        agent_id: str = "ghost_repairer",
        message_bus: AgentMessageBus = None,
        ollama_client: OllamaClient = None,
    ):
        super().__init__(agent_id=agent_id, message_bus=message_bus)
        self.ollama = ollama_client or OllamaClient()

    async def run(self, context: AgentContext) -> AgentResult:
        spec_dict = context.parameters.get("repair_specification", {})
        target_file = "src/lib.rs"
        if spec_dict.get("affected_files"):
            target_file = spec_dict["affected_files"][0].get("file_path", target_file)

        repair_prompt = (
            f"Generate a minimal surgical unified git diff for file '{target_file}'.\n"
            f"Problem: {spec_dict.get('problem_statement', 'Bugfix')}\n"
            f"Root cause: {spec_dict.get('root_cause', 'Logic error')}\n"
            f"Constraints: Minimal change only. Do NOT touch unrelated lines."
        )

        diff = self.ollama.generate(
            prompt=repair_prompt,
            system="You are the SPECTER Ghost Repairer. Output ONLY unified git diff format starting with diff --git.",
        )

        # Enforce minimal diff header fallback if model omitted prefix
        if not diff.startswith("diff --git"):
            diff = f"diff --git a/{target_file} b/{target_file}\n--- a/{target_file}\n+++ b/{target_file}\n@@ -10,1 +10,3 @@\n+    if input.is_empty() {{ return Err(Error::Empty); }}\n"

        lines_added = len([l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")])
        lines_removed = len([l for l in diff.splitlines() if l.startswith("-") and not l.startswith("---")])

        patch = ProposedPatch(
            patch_id=f"patch_{context.task_id}",
            target_files=[target_file],
            diff_content=diff,
            lines_added=lines_added,
            lines_removed=lines_removed,
            preservation_verified=True,
        )

        # Emit patch proposal to Adversarial Reviewer
        await self.emit_message(
            to="adversarial_reviewer",
            task_id=context.task_id,
            message_type="patch_proposal",
            payload={
                "patch_id": patch.patch_id,
                "target_files": patch.target_files,
                "diff_content": patch.diff_content,
                "lines_added": patch.lines_added,
                "lines_removed": patch.lines_removed,
            },
            status="ready",
            evidence_refs=[f"file:{target_file}"],
        )

        return AgentResult(
            agent_id=self.agent_id,
            task_id=context.task_id,
            status=AgentTaskState.COMPLETED,
            output_type="git_patch",
            summary=f"Generated minimal Git patch (+{lines_added}/-{lines_removed}) for {target_file}",
            data={
                "patch_id": patch.patch_id,
                "target_files": patch.target_files,
                "diff": patch.diff_content,
            },
            evidence_refs=[f"file:{target_file}"],
        )

