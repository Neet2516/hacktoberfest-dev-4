import os

os.makedirs('memory', exist_ok=True)

project_memory = """# SPECTER — Project Memory

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
"""

execution_state = """# SPECTER — Execution State

## 1. Current Phase
- **Current Phase**: Phase 1 — Architecture, Governance, and Task Engineering
- **Current Sprint**: Sprint 0 — Foundation & Governance
- **Execution Engine Status**: READY FOR INITIALIZATION

---

## 2. Task Allocation State
- **Total Backlog Tasks**: 130
- **READY Tasks**: 3 (`SPECTER-001`, `SPECTER-002`, `SPECTER-003`)
- **IN-PROGRESS Tasks**: 0
- **REVIEW Tasks**: 0
- **BLOCKED Tasks**: 0
- **COMPLETED Tasks**: 0

---

## 3. Quality Gate Status
| Gate | Description | Status | Verification Evidence |
|---|---|---|---|
| Gate 0.1 | Repository Discovery & Inventory | PASSED | Repository inspected; green-field status confirmed |
| Gate 0.2 | PRD Analysis & Requirement Mapping | PASSED | `docs/PROJECT_UNDERSTANDING.md` generated |
| Gate 0.3 | Agent Governance Infrastructure | PASSED | `agent/` charter, roles, protocols, prompts, schemas active |
| Gate 0.4 | Task Management System & Backlog | PASSED | 130 tasks indexed across 18 Epics with dependency graph |
| Gate 0.5 | Security Threat Modeling | PASSED | `docs/THREAT_MODEL.md` STRIDE analysis complete |
| Gate 1.0 | Implementation Authorization Gate | PENDING | Awaiting explicit human authorization to start EPIC 01 |

---

## 4. Active Workspaces
- Host Workspace: `c:\\Users\\ASUS\\OneDrive\\Desktop\\hacktoberfest-dev-4`
- Ephemeral Execution Workspaces: None active
- Docker Containers: None running
"""

architecture_decisions = """# SPECTER — Architecture Decision Records (ADRs)

## ADR-001: Rust & Axum for Backend API and Ingestion Services
- **Status**: Accepted
- **Context**: SPECTER requires high-performance file I/O for repository cloning, AST cache management, strict memory safety, and reliable API routing without runtime garbage collection pauses.
- **Decision**: Adopt Rust with the Axum web framework and SQLx for core backend services.
- **Consequences**: Extremely safe workspace isolation and fast concurrent request handling; requires maintaining FFI or RPC boundaries with Python agent runtime.
- **Alternatives Considered**: Go (lacks memory-safety guarantees at Rust's level), Node.js (high memory overhead on large codebases).

---

## ADR-002: Python for AI Agent Orchestration Runtime
- **Status**: Accepted
- **Context**: AI agent frameworks, Tree-sitter python bindings, Ollama clients, and prompt engineering utilities have their richest ecosystem in Python.
- **Decision**: Implement the agent runtime (all 6 agent roles and prompt pipelines) in Python 3.12 using AsyncIO.
- **Consequences**: Rapid iteration of prompt strategies and AST evaluations; must be decoupled from Rust services via REST/gRPC and Temporal activities.
- **Alternatives Considered**: Rust-only agents (ecosystem for prompt templating and LLM integration is less mature), TypeScript/LangChain (heavier dependencies).

---

## ADR-003: Temporal for Durable Workflow Orchestration
- **Status**: Accepted
- **Context**: Autonomous multi-agent cycles involve long-running activities, potential timeouts, LLM retries, and human approval gates that can take hours or days.
- **Decision**: Use Temporal as the central workflow orchestration engine.
- **Consequences**: Guarantees durable execution state, deterministic replay, automatic exponential backoff, and transparent pause/resume for human approvals.
- **Alternatives Considered**: Celery / Redis (fragile state tracking on worker crash), Custom DB State Machine (high development overhead, prone to race conditions).

---

## ADR-004: PostgreSQL with pgvector for Relational and Semantic Storage
- **Status**: Accepted
- **Context**: SPECTER needs ACID compliance for task states, audit logs, and message traces, as well as vector similarity search for Ghost Memory.
- **Decision**: Use PostgreSQL 16 with the `pgvector` extension as the single unified data store.
- **Consequences**: Simplifies operations by eliminating the need for a separate vector database (e.g. Pinecone, Milvus, Qdrant); transactional consistency across relational and vector data.
- **Alternatives Considered**: PostgreSQL + Pinecone (unnecessary cloud dependency), SQLite + Chroma (insufficient concurrency).

---

## ADR-005: Local Open-Weight Gemma via Ollama for LLM Inference
- **Status**: Accepted
- **Context**: Maintenance of open-source repositories must remain accessible, cost-effective, and fully private without leaking proprietary code to third-party cloud APIs.
- **Decision**: Standardize on Gemma 2 models executed locally via Ollama.
- **Consequences**: Zero API costs, total privacy, reproducibility across self-hosted environments; requires host hardware with sufficient VRAM/RAM (8GB-16GB+).
- **Alternatives Considered**: OpenAI / Anthropic APIs (violates air-gapped privacy principles, ongoing token costs).

---

## ADR-006: Disposable Docker Containers with Disabled Networking for Test Execution
- **Status**: Accepted
- **Context**: Untrusted code from abandoned repositories can execute arbitrary build scripts or malicious payloads during testing.
- **Decision**: Execute all build and test commands inside ephemeral, rootless Docker containers configured with `--network none` and strict CPU/RAM limits.
- **Consequences**: Absolute protection of host machine; prevents data exfiltration and SSRF attacks; requires pre-caching dependencies or multi-stage container builds.
- **Alternatives Considered**: Running directly on host (unacceptable security hazard), Full VMs (too slow and resource-heavy).

---

## ADR-007: Tree-sitter for Multi-Language Syntax Parsing
- **Status**: Accepted
- **Context**: SPECTER must parse and analyze code across C, Rust, Go, Python, JavaScript, and TypeScript without invoking language-specific compiler toolchains.
- **Decision**: Integrate Tree-sitter grammars in the Repository Archaeologist.
- **Consequences**: Fast, robust concrete syntax tree (CST) generation resilient to syntax errors in legacy code.
- **Alternatives Considered**: Regex parsing (inaccurate, brittle), Compiler frontends (too heavy, require full toolchains).

---

## ADR-008: Structured JSON Schema Message Bus (A2A-Inspired)
- **Status**: Accepted
- **Context**: Unstructured natural language chat between agents leads to hallucinations, dropped constraints, and untraceable states.
- **Decision**: Require all inter-agent communication to use strictly typed JSON messages validated against draft-07 JSON schemas.
- **Consequences**: Deterministic parsing, clear schema validation errors, complete auditability.
- **Alternatives Considered**: Unstructured markdown conversations (unreliable, non-reproducible).

---

## ADR-009: Mandatory Human Approval Gate Prior to Remote VCS Mutations
- **Status**: Accepted
- **Context**: Autonomous agents pushing untested or unwanted branches/PRs to GitHub harms repository reputation and creates security risks.
- **Decision**: Enforce an unbypassable human approval gate before any branch creation, commit push, or pull request creation.
- **Consequences**: Total human control over remote actions; prevents spam and accidental code corruption.
- **Alternatives Considered**: Fully autonomous PR creation (violates safety policy and PRD Section 11).

---

## ADR-010: Model Context Protocol (MCP) for Agent Tool Contracts
- **Status**: Accepted
- **Context**: Agents require access to external capabilities (Git, Tree-sitter, PostgreSQL, Docker) with least-privilege scoping.
- **Decision**: Expose tools to agents via Model Context Protocol (MCP) servers with capability enforcement.
- **Consequences**: Standardized tool calling, strict capability boundaries, pluggable architecture.
- **Alternatives Considered**: Hardcoded Python function calls (lacks isolation and modularity).
"""

verified_facts = """# SPECTER — Verified Facts

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
"""

blockers = """# SPECTER — Technical Blockers & Architectural Questions

The following blockers, unresolved questions, and environmental dependencies must be addressed before or during initial implementation sprints:

| Blocker ID | Category | Description | Impact | Required Action / Owner |
|---|---|---|---|---|
| `BLK-001` | Infrastructure | Local Docker Engine availability and rootless container permissions on Windows host | Blocks EPIC 12 (Test execution sandbox) | Verify Docker Desktop / WSL2 engine status (DevOps) |
| `BLK-002` | Infrastructure | Local Temporal Server instance deployment method (Docker Compose vs local binary) | Blocks EPIC 13 (Workflow orchestration) | Finalize Temporal service in `docker-compose.yml` (DevOps) |
| `BLK-003` | LLM Runtime | Target Gemma 2 model size selection (Gemma 2 9B vs Gemma 2 27B) based on available GPU VRAM | Blocks EPIC 06 (AI agent runtime performance) | Benchmark inference latency & memory consumption (AI Lead) |
| `BLK-004` | Security | Secure vault implementation for GitHub personal access tokens (never in prompts or logs) | Blocks EPIC 05 (GitHub integration) | Select token encryption strategy (e.g. OS keyring, HashiCorp Vault, or encrypted PG column) (Security Lead) |
| `BLK-005` | Data Store | PostgreSQL 16 `pgvector` extension compilation/image for Windows/Docker Compose | Blocks EPIC 01 & 08 (Ghost Memory) | Use official `pgvector/pgvector:pg16` Docker image (DevOps) |
| `BLK-006` | Code Analysis | Tree-sitter language grammar bundle compilation across Windows and Linux environments | Blocks EPIC 04 (Repository Archaeology) | Pin pre-compiled python Tree-sitter wheels for C, Rust, Go, Python, TS (Architect) |
| `BLK-007` | Test Sandbox | Pre-caching base language images (Rust, Python, Node) to support `--network none` testing | Blocks EPIC 12 (Offline container test execution) | Design base container cache volume strategy (DevOps) |
| `BLK-008` | VCS | Rate limiting strategy for unauthenticated vs authenticated GitHub REST/GraphQL API | Blocks EPIC 03 & 05 (Repository ingestion) | Implement token rotation or strict client-side rate limiter (Backend Lead) |
| `BLK-009` | Communication | Rust-to-Python IPC transport mechanism (gRPC vs REST over Unix sockets/localhost) | Blocks EPIC 02 / EPIC 06 integration | Standardize on lightweight REST HTTP/2 or gRPC between services (Architect) |
| `BLK-010` | Frontend | React Flow license and component bundle size optimization for pipeline visualization | Blocks EPIC 15 (Frontend dashboard) | Verify React Flow MIT license and configure dynamic import (Frontend Lead) |
| `BLK-011` | Fixtures | Selection of official demo repository for Hacktoberfest scenario walkthrough | Blocks EPIC 17 (Automated demo testing) | Select and fork a lightweight, abandoned open-source repo with known reproducible bug (Product Owner) |
| `BLK-012` | Agent Protocol | Max context token window handling for large repository file ingestion into Gemma prompts | Blocks EPIC 04 & 09 (Archaeologist & Investigator) | Implement AST chunking and vector retrieval filtering before prompt injection (AI Lead) |
| `BLK-013` | Orchestration | Temporal Python SDK vs Rust SDK role distribution | Blocks EPIC 13 (Temporal activities) | Temporal Python SDK for agent activities, Rust SDK or REST for coordinator signals (Architect) |
| `BLK-014` | Governance | Exact criteria for determining when a patch diff is "minimal" vs "over-refactored" | Blocks EPIC 11 (Adversarial Reviewer) | Define AST delta metrics (e.g., modified AST nodes <= 1.2x of affected scope) (Architect) |
| `BLK-015` | Security | Sanitization rules for malicious ANSI escape codes and terminal exploits in test container output | Blocks EPIC 12 & 15 (Test output display) | Implement ANSI stripping and regex sanitization filter (Security Lead) |
| `BLK-016` | UI/UX | Real-time agent streaming updates protocol (WebSocket vs Server-Sent Events SSE) | Blocks EPIC 15 (Agent live feed) | Standardize on Server-Sent Events (SSE) from Axum backend (Frontend Lead) |
| `BLK-017` | Storage | Workspace disk quota enforcement policy (preventing disk exhaustion on large git clones) | Blocks EPIC 03 (Repository Ingestion) | Set 500MB max workspace quota with shallow clone (`--depth 100`) (Backend Lead) |
| `BLK-018` | Ghost Memory | Vector similarity distance metric (cosine vs inner product) and embedding model selection | Blocks EPIC 08 (Ghost Memory) | Use `nomic-embed-text` or `all-MiniLM-L6-v2` via Ollama/SentenceTransformers (AI Lead) |
| `BLK-019` | CI/CD | GitHub Actions self-hosted vs cloud runner requirements for Docker-in-Docker workflows | Blocks EPIC 01 (CI/CD pipeline) | Configure GitHub Actions matrix with Ubuntu-latest Docker daemon (DevOps) |
| `BLK-020` | Compliance | AI Code Disclosure & License compliance tracking for generated patches (Hacktoberfest rules) | Blocks EPIC 14 (PR generation) | Include explicit AI disclosure badge and original repo license preservation in PR template (Product Owner) |
"""

session_handoff = """# SPECTER — Session Handoff

## 1. Session Information
- **Session Date**: 2026-10-31
- **Session Type**: Phase 1 — Comprehensive Architecture, Agent Governance, and Task Management Establishment
- **Architect Lead**: Principal AI Systems Architect & Agent Engineering Lead
- **Status**: PHASE 1 COMPLETE. System governance and task backlog fully operational.

---

## 2. Deliverables Produced in This Session

### A. Documentation Layer (`docs/`)
1. `docs/PRD.md`: Original product requirements document preserved.
2. `docs/PROJECT_UNDERSTANDING.md`: Detailed PRD analysis, requirement mapping, and gap audit.
3. `docs/TECHNICAL_ARCHITECTURE.md`: Complete system architecture, component specs, database models, and API contracts.
4. `docs/THREAT_MODEL.md`: Exhaustive STRIDE security threat model and attack surface analysis.
5. `docs/WORKFLOW_GUIDE.md`: Step-by-step operational workflows, state machines, and example artifacts.

### B. Agent Governance & Operational Framework (`agent/`)
1. Core Governance: `AGENT_CHARTER.md`, `SYSTEM_ARCHITECTURE.md`, `EXECUTION_PROTOCOL.md`, `FAILURE_RECOVERY.md`, `QUALITY_GATES.md`, `SAFETY_POLICY.md`, `TOOL_CONTRACTS.md`.
2. Registry: `agent/registry/AGENT_REGISTRY.md`, `AGENT_CAPABILITIES.md`, `AGENT_DEPENDENCIES.md`.
3. Agent Roles: `agent/roles/COORDINATOR.md`, `REPOSITORY_ARCHAEOLOGIST.md`, `ISSUE_INVESTIGATOR.md`, `GHOST_REPAIRER.md`, `ADVERSARIAL_REVIEWER.md`, `TEST_ENGINEER.md`.
4. Communication Protocols: `agent/protocols/MESSAGE_PROTOCOL.md`, `DELEGATION_PROTOCOL.md`, `HANDOFF_PROTOCOL.md`, `APPROVAL_PROTOCOL.md`, `ESCALATION_PROTOCOL.md`.
5. Prompts: `agent/prompts/SYSTEM_PROMPTS.md`, `INVESTIGATION_PROMPTS.md`, `REPAIR_PROMPTS.md`, `REVIEW_PROMPTS.md`, `TESTING_PROMPTS.md`.
6. JSON Schemas: `agent/schemas/agent-message.schema.json`, `task.schema.json`, `agent-output.schema.json`, `review-report.schema.json`.

### C. Persistent Memory (`memory/`)
1. `memory/PROJECT_MEMORY.md`: Project mission, stack, and context.
2. `memory/EXECUTION_STATE.md`: Execution state and quality gate tracking.
3. `memory/ARCHITECTURE_DECISIONS.md`: 10 foundational ADRs.
4. `memory/VERIFIED_FACTS.md`: Experimentally verified ground truths.
5. `memory/BLOCKERS.md`: 20 actionable technical blockers.
6. `memory/SESSION_HANDOFF.md`: Current handoff brief.

### D. Task Management Framework (`tasks/`)
1. `tasks/README.md`: Operational manual for task lifecycle and state transitions.
2. `tasks/TASK_TEMPLATE.md`: Standard 20-field task template.
3. `tasks/TASK_INDEX.md`: Master index of all 130 implementation tasks across 18 epics.
4. `tasks/DEPENDENCY_GRAPH.md`: Dependency topology and critical path visualization.
5. Lifecycle Directories: `tasks/backlog/`, `tasks/ready/`, `tasks/in-progress/`, `tasks/review/`, `tasks/completed/`, `tasks/blocked/`.

---

## 3. Recommended First Five Implementation Tasks
Upon receiving human authorization to commence implementation, the development team must execute the following top-priority foundational tasks:

1. **`SPECTER-001`**: Initialize Rust Axum API service skeleton (Priority: P0, Owner: Human/DevOps, Dependencies: None).
2. **`SPECTER-002`**: Initialize Python agent runtime package (Priority: P0, Owner: Human/DevOps, Dependencies: None).
3. **`SPECTER-003`**: Initialize Next.js + TypeScript frontend project (Priority: P0, Owner: Frontend Developer, Dependencies: None).
4. **`SPECTER-004`**: Configure Docker Compose for development environment (Priority: P0, Owner: Human/DevOps, Dependencies: SPECTER-001, SPECTER-002, SPECTER-003).
5. **`SPECTER-005`**: Set up PostgreSQL with pgvector extension (Priority: P0, Owner: Human/DevOps, Dependencies: SPECTER-004).

---

## 4. Immediate Files Requiring Attention
- `tasks/ready/SPECTER-001.md`, `SPECTER-002.md`, `SPECTER-003.md` (to begin Sprint 1 implementation).
- `memory/BLOCKERS.md` (DevOps and AI Lead to resolve `BLK-001`, `BLK-003`, and `BLK-005`).
"""

files = {
    'memory/PROJECT_MEMORY.md': project_memory,
    'memory/EXECUTION_STATE.md': execution_state,
    'memory/ARCHITECTURE_DECISIONS.md': architecture_decisions,
    'memory/VERIFIED_FACTS.md': verified_facts,
    'memory/BLOCKERS.md': blockers,
    'memory/SESSION_HANDOFF.md': session_handoff
}

for path, content in files.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created {path}")

print("All 6 memory files written successfully.")

