import os
import json
from typing import Dict, Any, List

from ..base import SpecterAgent
from ..context import AgentContext, AgentResult, AgentTaskState
from ..message_bus import AgentMessageBus
from ..archaeology.parser import CodeParser
from ..archaeology.analyzer import (
    ReadmeAnalyzer,
    DependencyExtractor,
    PatternDetector,
    RepositoryContextReport,
)
from ..llm.client import OllamaClient

class RepositoryArchaeologistAgent(SpecterAgent):
    """Specialized AI Agent that reconstructs historical decisions and analyzes codebase structure."""

    def __init__(
        self,
        agent_id: str = "repository_archaeologist",
        message_bus: AgentMessageBus = None,
        ollama_client: OllamaClient = None,
    ):
        super().__init__(agent_id=agent_id, message_bus=message_bus)
        self.code_parser = CodeParser()
        self.ollama = ollama_client or OllamaClient()

    async def run(self, context: AgentContext) -> AgentResult:
        ws_path = context.workspace_path
        repo_files = []
        detected_languages = set()
        dependencies = []
        readme_insights = None

        if os.path.exists(ws_path):
            for root, _, files in os.walk(ws_path):
                if ".git" in root or "node_modules" in root or "target" in root:
                    continue
                for f in files:
                    rel_path = os.path.relpath(os.path.join(root, f), ws_path).replace("\\", "/")
                    repo_files.append(rel_path)

                    # Language detection
                    lang = self.code_parser.detect_language(rel_path)
                    if lang:
                        detected_languages.add(lang)

                    # README analysis
                    if f.lower().startswith("readme") and not readme_insights:
                        try:
                            with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as rf:
                                readme_insights = ReadmeAnalyzer.analyze(rf.read())
                        except Exception:
                            pass

                    # Manifest parsing
                    if f.lower() in ["cargo.toml", "package.json", "requirements.txt"]:
                        try:
                            with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as mf:
                                dep_inv = DependencyExtractor.extract_from_manifest(f, mf.read())
                                if dep_inv:
                                    dependencies.append(dep_inv)
                        except Exception:
                            pass

        primary_languages = sorted(list(detected_languages)) or ["Rust", "Python"]
        pattern = PatternDetector.detect_pattern(repo_files, primary_languages)

        # Synthesize historical insights via Ollama / Gemma
        archaeology_prompt = (
            f"Analyze repository architecture for codebase with languages: {primary_languages}, "
            f"detected pattern: {pattern}. Provide historical maintainer insights and architectural style."
        )
        llm_synthesis = self.ollama.generate(
            prompt=archaeology_prompt,
            system="You are the SPECTER Repository Archaeologist. Output valid JSON.",
        )

        report = RepositoryContextReport(
            repo_name=context.parameters.get("repo_name", "unnamed-repo"),
            primary_languages=primary_languages,
            architecture_pattern=pattern,
            build_system=dependencies[0].package_manager if dependencies else "cargo",
            test_framework="cargo test / pytest",
            dependencies=dependencies,
            readme_insights=readme_insights,
            historical_summary=llm_synthesis,
            unresolved_smells=[],
        )

        # Emit structured A2A message to Coordinator
        await self.emit_message(
            to="resurrection_coordinator",
            task_id=context.task_id,
            message_type="repository_context",
            payload={
                "primary_languages": primary_languages,
                "architecture_pattern": pattern,
                "build_system": report.build_system,
                "synthesis": llm_synthesis,
            },
            status="completed",
            evidence_refs=[f"git:commit:{context.baseline_commit or 'HEAD'}"],
        )

        return AgentResult(
            agent_id=self.agent_id,
            task_id=context.task_id,
            status=AgentTaskState.COMPLETED,
            output_type="context_report",
            summary=f"Reconstructed repository architecture ({pattern}) with {len(primary_languages)} primary languages.",
            data={
                "languages": primary_languages,
                "pattern": pattern,
                "dependencies_count": len(dependencies),
            },
            evidence_refs=[f"git:commit:{context.baseline_commit or 'HEAD'}"],
        )
