# SPECTER — Verified Facts

> **CRITICAL DIRECTIVE**: Only experimentally, programmatically, or independently verified facts may be recorded in this document. Never record an unverified AI assumption or aspiration as a verified fact.

---

## 1. Verified Repository State
- **Verification Date**: 2026-10-31
- **Method of Verification**: Direct filesystem traversal (`Get-ChildItem -Recurse -Force`) and shell inspection.
- **Facts Established**:
  1. The project repository was initialized with a `.git` directory and a single documentation file: `docs/PRD.md` (10,011 bytes).
  2. Prior to this planning session, NO source code directories existed (`agent/`, `memory/`, `tasks/`, `src/`, `frontend/`, `backend/` were absent).
  3. The local execution environment is Windows with PowerShell 5.1/7.x and Python 3.12.11 installed.
  4. The project is an MVP for the Hacktoberfest 2026 challenge: "Ghost in the Machine".
  5. The product tagline documented in PRD line 4 is: *"Every abandoned repository deserves another life."*

---

## 2. Verified Technical Constraints
- **Docker Isolation**: Host execution of repository build scripts is strictly prohibited by PRD Section 11.
- **Approval Gate**: PRD FR-13 explicitly mandates human approval prior to branch or PR creation.
- **Agent Count**: Exactly 6 agent roles are specified in the PRD (Archaeologist, Investigator, Repairer, Reviewer, Test Engineer, Coordinator).
- **Core Technology Stack**: Next.js, Rust/Axum, Python, Temporal, PostgreSQL + pgvector, Docker, Tree-sitter, Ollama/Gemma.

---

## 3. Verified System Assets (Generated in Planning Session)
- **Agent Governance Layer**: Complete set of 30 files generated under `agent/` including charter, system architecture, execution protocol, failure recovery, quality gates, safety policy, tool contracts, registry, roles, protocols, prompts, and JSON schemas.
- **Task Management Framework**: 130 backlog tasks defined across 18 epics in `tasks/TASK_INDEX.md`, lifecycle directories established (`backlog`, `ready`, `in-progress`, `review`, `completed`, `blocked`), and `tasks/DEPENDENCY_GRAPH.md` established.
- **Documentation**: Comprehensive architecture, threat model, and workflow guide established in `docs/`.
