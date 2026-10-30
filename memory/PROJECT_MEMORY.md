# SPECTER — Project Memory

## 1. Project Context & Mission
- **Project Name**: SPECTER — The Ghost Maintainer
- **Tagline**: *"Every abandoned repository deserves another life."*
- **Challenge**: Hacktoberfest 2026 — Ghost in the Machine
- **Version**: 1.0 — MVP
- **Core Problem**: Thousands of open-source repositories languish in inactivity when maintainers step away. Context disappears, bugs rot, and new contributors struggle.
- **Product Vision**: An autonomous multi-agent AI maintenance system acting as digital successor to missing maintainers. SPECTER reconstructs historical architecture, investigates reproducible issues, writes minimal surgical patches, independently audits for regressions, tests inside isolated Docker containers, and prepares pull requests for human approval.

---

## 2. Technology Stack Summary
| Layer | Chosen Technology | Architectural Role |
|---|---|---|
| Frontend | Next.js (TypeScript), Tailwind CSS, shadcn/ui, React Flow | Maintainer dashboard, agent pipeline graph, diff viewer |
| Backend Services | Rust, Axum, SQLx | High-performance, memory-safe API, workspace filesystem manager, rate limiting |
| Agent Orchestration | Python 3.12, AsyncIO | Specialized agent reasoning, prompt lifecycle, Tree-sitter bindings |
| Workflow Durability | Temporal (Temporal Server & SDKs) | Resilient state machines, deterministic replay, activity timeouts, crash recovery |
| Database & Vector | PostgreSQL 16 + pgvector | Task states, agent message history, audit logs, Ghost Memory vector embeddings |
| Model Inference | Gemma 2 (9B/27B) via Ollama | Local open-weight LLM execution with zero external data leakage |
| AST & Analysis | Tree-sitter | Deterministic multi-language code parsing, symbol mapping, call graph extraction |
| Execution Sandbox | Docker Engine | Disposable rootless containers with network disabled (`network: none`) for testing |
| VCS Integration | Git CLI, GitHub REST/GraphQL API | Read-only analysis, branch & PR creation exclusively post-approval |

---

## 3. Agent Roster & Identities
1. **Resurrection Coordinator** (`resurrection_coordinator`): Workflow orchestration, state tracking, approval enforcement.
2. **Repository Archaeologist** (`repository_archaeologist`): Git history mining, AST inspection, architectural memory building.
3. **Issue Investigator** (`issue_investigator`): Issue reproduction, root cause deduction, repair specification generation.
4. **Ghost Repairer** (`ghost_repairer`): Minimal patch generation, preservation constraint enforcement.
5. **Adversarial Reviewer** (`adversarial_reviewer`): Independent audit, regression detection, security scanning.
6. **Test Engineer** (`test_engineer`): Test runner discovery, isolated Docker verification execution.

---

## 4. Current Implementation State
- **Phase**: Phase 1 — Project Understanding, Agent Governance & Task Architecture.
- **Implemented Components**: None (Strictly Green-field). No application code or backend services have been built yet.
- **Completed Deliverables**:
  - Comprehensive PRD analysis (`docs/PROJECT_UNDERSTANDING.md`).
  - Technical architecture & threat model (`docs/TECHNICAL_ARCHITECTURE.md`, `docs/THREAT_MODEL.md`).
  - Operational workflow guides (`docs/WORKFLOW_GUIDE.md`).
  - Complete agent governance charter, roles, protocols, prompts, and JSON schemas (`agent/`).
  - Master task index containing 130 structured tasks across 18 epics (`tasks/`).
