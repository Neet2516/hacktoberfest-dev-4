# SPECTER — Agent Developer Guide

## 1. Architecture Overview
SPECTER coordinates 6 specialized autonomous AI agents:
1. **Resurrection Coordinator**: Oversees pipeline lifecycle, retries, and human signoff.
2. **Repository Archaeologist**: Analyzes legacy codebases, manifests, and historical git commits.
3. **Issue Investigator**: Dissects GitHub issues, pinpoints root causes, and generates repair specs.
4. **Ghost Repairer**: Generates minimal, scoped unified diffs honoring past author idioms.
5. **Adversarial Reviewer**: Audits proposed diffs for regression risks, security flaws, and over-refactoring.
6. **Test Engineer**: Executes test suites inside unprivileged `--network none` Docker sandboxes.

## 2. Implementing a New Agent
All agents extend `SpecterAgent`:
```python
from specter_runtime.base import SpecterAgent
from specter_runtime.context import AgentContext, AgentResult, AgentTaskState

class CustomSpecialistAgent(SpecterAgent):
    async def run(self, context: AgentContext) -> AgentResult:
        # 1. Inspect parameters
        # 2. Invoke least-privilege MCP tools
        # 3. Emit structured A2A message
        await self.emit_message(to="coordinator", ...)
        return AgentResult(...)
```
