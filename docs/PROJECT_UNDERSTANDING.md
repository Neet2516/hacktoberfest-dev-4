# SPECTER — Project Understanding Report

> **Document Status:** Planning Phase — Initial Analysis  
> **Version:** 0.1.0  
> **Date:** 2026-10-31  
> **Author:** Documentation Layer — Generated from PRD Analysis  
> **Source:** docs/PRD.md (v1.0 MVP)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [PRD Analysis](#2-prd-analysis)
3. [Technology Stack Analysis](#3-technology-stack-analysis)
4. [Agent Architecture Analysis](#4-agent-architecture-analysis)
5. [Architectural Observations](#5-architectural-observations)
6. [Identified Ambiguities and Open Questions](#6-identified-ambiguities-and-open-questions)
7. [Identified Risks](#7-identified-risks)
8. [Initial Architecture Decisions Recommended](#8-initial-architecture-decisions-recommended)
9. [Recommended First Implementation Tasks](#9-recommended-first-implementation-tasks)

---

## 1. Executive Summary

### What SPECTER Is

SPECTER — The Ghost Maintainer — is an AI-powered autonomous repository maintenance system. It accepts a public GitHub repository URL, deploys a team of six specialized AI agents, and works through a structured pipeline to: analyze the codebase, investigate a selected issue, generate a minimal code patch, review it adversarially, execute tests in isolation, and — after explicit human approval — create a GitHub pull request.

SPECTER's signature feature is **Ghost Memory**: a persistent, per-repository knowledge base powered by vector similarity search (pgvector) that accumulates architectural context, historical bug fixes, rejected approaches, and verified patches. This memory makes SPECTER progressively more effective at maintaining a repository over time, in contrast to stateless AI coding assistants.

The project is entering the **Hacktoberfest 2026 "Ghost in the Machine" hackathon challenge**.

### Current State

This is a **green-field project**. As of 2026-10-31, the only file that exists in the repository is `docs/PRD.md`. No code, no directory structure, no tests, no configuration files have been created. The project is in the documentation and planning phase.

### What Needs to Be Built

Everything. The full list:
1. **Frontend** — Next.js 14+ application with React Flow agent graph, diff viewer, approval gate UI
2. **API Backend** — Rust/Axum service with REST endpoints, WebSocket hub, token vault, audit log
3. **Agent Runtime** — Python package with 6 agent implementations, MCP tool layer, Ollama client
4. **Temporal Workflows** — Python workflow definitions, activity implementations, retry policies
5. **Database** — PostgreSQL schema with pgvector extension, all migrations
6. **Docker Sandbox** — Container lifecycle management, resource limits, security hardening
7. **GitHub Integration** — API client, token proxy, branch + PR creation
8. **Observability** — OpenTelemetry instrumentation, Prometheus metrics, Jaeger tracing
9. **Infrastructure** — Docker Compose configuration, environment management
10. **Demo Fixtures** — Pre-built faulty patch, target demo repository selection

---

## 2. PRD Analysis

### 2.1 Functional Requirements Analysis

| FR-ID | Requirement | Complexity | MVP? | Implementation Notes |
|---|---|---|---|---|
| FR-01 | Accept a public GitHub repository URL | Low | ✅ Yes | URL validation, SSRF protection required |
| FR-02 | Clone the repository into an isolated workspace | Low | ✅ Yes | `git clone` via subprocess; workspace on Docker volume |
| FR-03 | Analyze source code and repository history | High | ✅ Yes | Tree-sitter + Git log + LLM synthesis |
| FR-04 | Retrieve and process selected GitHub issues | Medium | ✅ Yes | GitHub REST API via Rust service proxy |
| FR-05 | Execute specialized AI agents | High | ✅ Yes | Temporal activities, Ollama, 6 agent implementations |
| FR-06 | Support structured agent-to-agent communication | Medium | ✅ Yes | Pydantic message schemas, PostgreSQL bus, WebSocket fan-out |
| FR-07 | Generate proposed code patches | High | ✅ Yes | LLM → unified diff → validation |
| FR-08 | Independently review patches | High | ✅ Yes | Adversarial Reviewer with separate LLM context |
| FR-09 | Execute tests inside isolated Docker environment | High | ✅ Yes | Docker API, rootless containers, resource limits |
| FR-10 | Maintain persistent repository memory | High | ✅ Yes | pgvector, embedding pipeline, nomic-embed-text |
| FR-11 | Display agent activity and execution history | Medium | ✅ Yes | React Flow graph, WebSocket streaming, audit log UI |
| FR-12 | Generate a human-readable maintenance report | Low | ✅ Yes | Structured template from agent outputs |
| FR-13 | Create a GitHub branch and pull request after explicit approval | Medium | ✅ Yes | Temporal approval gate (signal-based), GitHub API |
| FR-14 | Recover from agent failures using persisted task state | Medium | ✅ Yes | Temporal durable execution, activity idempotency |

### 2.2 Non-Functional Requirements Analysis

| NFR | Implementation Approach | Risk |
|---|---|---|
| Security-first repository execution | Docker isolation, read-only mounts, no network in containers | Medium — container escape is a residual risk |
| No automatic merging | Temporal approval gate (signal required) | Low — well-supported by Temporal |
| No unrestricted credential access | Rust vault, token never sent to agents | Low |
| Reproducible agent execution | Temporal replay, fixed model versions, deterministic prompts | Medium — LLMs are non-deterministic |
| Persistent workflow state | Temporal + PostgreSQL | Low |
| Clear failure reporting | Structured error messages, audit log | Low |
| Structured logs and traces | OpenTelemetry, structlog | Low |
| Modular agent architecture | Abstract `SpectreAgent` base class | Low |
| Local open-weight AI | Ollama + Gemma | Low (Ollama is mature) |
| Configurable resource limits | Docker API parameters, environment variables | Low |

### 2.3 MVP Scope vs. Full Scope

**MVP (required for Hacktoberfest submission):**
- Single repository at a time
- One issue per task
- Three core agents: Archaeologist, Repairer, Reviewer (plus Test Engineer and Coordinator as workflow stages)
- Python as the primary supported language (given Tree-sitter grammar maturity)
- Gemma 3 12B as the LLM (configurable)
- Basic Ghost Memory (write during archaeology, read during repair)
- Manual Docker Compose deployment

**Post-MVP (out of scope for Hacktoberfest):**
- Multi-repository parallelism
- Additional language grammars (all languages equally)
- Self-modifying agents
- Web-hosted deployment with multi-tenant user accounts
- Webhook-triggered maintenance (automatic issue detection)
- Financial/crypto integrations

### 2.4 Out-of-Scope Items (PRD Section 13)

The PRD explicitly excludes:
1. Autonomous repository discovery at scale
2. Automatic PR merging
3. Equal support for all programming languages
4. Self-modifying agents
5. Autonomous production deployment
6. Financial or cryptocurrency integrations
7. Unrestricted agent-to-agent network discovery

---

## 3. Technology Stack Analysis

### 3.1 Next.js (Frontend)

**Role:** User interface for repository management, agent activity monitoring, patch review, and PR approval.

**Integration Points:** REST API (Tanstack Query), WebSocket (agent messages), SSE (log streaming)

**Potential Risks:**
- React Flow performance with many agent message edges (dozens of messages per task)
- WebSocket reconnection handling if the server restarts mid-task

**Alternatives Considered:** SvelteKit (lighter), Vue 3 (ecosystem), plain React (more control). Next.js chosen for its App Router, server components for initial data loading, and strong TypeScript ecosystem.

---

### 3.2 Rust / Axum (Backend API)

**Role:** Security boundary between the untrusted external world and the internal agent system. Holds the GitHub token, enforces rate limits, writes the audit log, proxies Docker status.

**Integration Points:** PostgreSQL (SQLx), Temporal (gRPC SDK), Docker API (HTTP), GitHub API (HTTPS), Frontend (REST + WebSocket)

**Potential Risks:**
- Rust compile times slow CI feedback loops
- Axum's ecosystem is younger than Express or FastAPI — some middleware may need to be written from scratch

**Alternatives Considered:** Go/Gin (simpler, but GC pauses), Node.js/Fastify (runtime safety concerns given security role), Python/FastAPI (too close to agent runtime for separation of concerns). Rust chosen for memory safety in the security-critical gateway role.

---

### 3.3 Python / Temporalio (Agent Runtime)

**Role:** Executes all six AI agents. Each agent is a Temporal activity.

**Integration Points:** Ollama (HTTP), PostgreSQL (asyncpg), Tree-sitter (C bindings), Docker API (docker Python SDK), GitHub (httpx)

**Potential Risks:**
- Python's Global Interpreter Lock (GIL) limits true parallelism (asyncio mitigates for I/O-bound agent work)
- Tree-sitter Python bindings can be finicky with newer Python versions
- Ollama cold-start time for large models (12B+) can be 30–60 seconds

**Alternatives Considered:** Node.js (weaker AI tooling), Go (no mature LLM agent frameworks). Python chosen for richest AI/ML ecosystem.

---

### 3.4 Temporal (Workflow Engine)

**Role:** Durable execution of the multi-step maintenance workflow. Provides retry policies, timeouts, and the approval signal gate.

**Integration Points:** PostgreSQL (Temporal uses its own schema), Python SDK (agent activities), Rust SDK (signal sending from API)

**Potential Risks:**
- Temporal adds operational complexity (separate service)
- Temporal's Python SDK requires careful handling of determinism in workflow code
- Cold start: Temporal server takes ~30 seconds to be ready after Docker Compose start

**Alternatives Considered:** Celery (less durable, no built-in signal/query mechanism), Prefect (Python-only server-side), custom state machine in PostgreSQL (no built-in durability/retry). Temporal chosen for FR-14 (failure recovery) and the approval gate requirement.

---

### 3.5 PostgreSQL + pgvector

**Role:** Single data store for all SPECTER data. pgvector extension enables vector similarity search for Ghost Memory.

**Integration Points:** All services connect via connection pool.

**Potential Risks:**
- pgvector HNSW index requires tuning (`m`, `ef_construction`) for good recall vs. speed trade-off
- PostgreSQL connection limits with multiple services and Temporal's own connection pool — use PgBouncer in production

**Alternatives Considered:** PostgreSQL + Pinecone/Weaviate (separate vector DB adds synchronization complexity), MongoDB Atlas (operational simplicity but less mature vector search). Single PostgreSQL instance chosen to keep the stack simple for the hackathon MVP.

---

### 3.6 Gemma via Ollama

**Role:** Local LLM inference for all agent reasoning tasks (repository analysis, issue investigation, patch generation, adversarial review).

**Integration Points:** Python agent runtime (HTTP client to Ollama server)

**Potential Risks:**
- Gemma 3 12B requires ~10 GB VRAM — demo hardware must be verified
- Non-determinism: same prompt can produce different outputs on each run
- Gemma's coding ability on some languages (e.g., older Fortran) is limited

**Alternatives Considered:** OpenAI GPT-4o (privacy concern — repository code sent externally), Anthropic Claude (same privacy concern), Llama 3 (strong coding benchmark but license considerations), Mistral (good coding but less Google ecosystem alignment). Gemma + Ollama chosen for local inference (security requirement) and Google alignment.

---

### 3.7 Tree-sitter

**Role:** Parse source code into concrete syntax trees for symbol extraction, impact analysis, and patch validation without executing the code.

**Integration Points:** Python agent runtime (Python bindings)

**Potential Risks:**
- Grammar availability varies by language — not all Tree-sitter grammars are production-ready
- Python bindings have occasional compilation issues on Windows development machines (see BLK-009)

**Alternatives Considered:** Language-specific AST tools (each language has its own: `ast` in Python, TypeScript compiler API, etc.) — too fragmented. Regex-based analysis — brittle. Tree-sitter chosen for language-agnostic CST parsing.

---

### 3.8 Docker (Test Isolation)

**Role:** Provides an isolated, disposable execution environment for running repository tests. Prevents repository code from executing on the host.

**Integration Points:** Rust API (Docker API client for container lifecycle), Python Test Engineer agent (requests test execution via API), Docker volume for workspace sharing

**Potential Risks:**
- Docker-in-Docker is intentionally not used (security), which means test containers cannot themselves spawn Docker containers
- Rootless Docker requires configuration on some Linux distributions
- Windows Docker (Docker Desktop) has different isolation properties than Linux Docker

**Alternatives Considered:** Firecracker microVMs (stronger isolation, much higher setup complexity), gVisor (strong isolation, compatible with Docker), chroot jails (insufficient isolation). Docker chosen for maturity and ecosystem. gVisor can be added as a security enhancement post-MVP.

---

### 3.9 React Flow + shadcn/ui

**Role:** Frontend visualization of agent communication graph. shadcn/ui for base UI components.

**Integration Points:** WebSocket (receive agent messages as graph edges), Zustand (graph state)

**Potential Risks:**
- React Flow can have performance issues with > 50 nodes — agent graph per task will be < 20 nodes, so not a concern
- shadcn/ui components require Tailwind CSS v3 — version compatibility to confirm

---

## 4. Agent Architecture Analysis

### 4.1 Agent Responsibilities Mapped to FRs

| Agent | Primary FRs | Secondary FRs |
|---|---|---|
| Repository Archaeologist | FR-03, FR-10 | FR-11 |
| Issue Investigator | FR-04, FR-03 | FR-10, FR-11 |
| Ghost Repairer | FR-07 | FR-06, FR-10, FR-11 |
| Adversarial Reviewer | FR-08 | FR-06, FR-10, FR-11 |
| Test Engineer | FR-09 | FR-06, FR-11 |
| Resurrection Coordinator | FR-05, FR-06, FR-14 | FR-12, FR-13, FR-11 |

### 4.2 Communication Model Understanding

The A2A communication model uses a database-backed message bus (PostgreSQL `agent_messages` table) with WebSocket fan-out for real-time display. This is a sensible hybrid:

- **Persistence:** Messages survive crashes (PostgreSQL)
- **Real-time:** Messages appear in the UI immediately (WebSocket)
- **Validation:** Schema enforced by Pydantic before persistence

The key insight: messages flow through the Resurrection Coordinator, which acts as the message broker. No agent talks directly to another agent without the Coordinator's knowledge.

### 4.3 Ghost Memory as the Signature Feature

Ghost Memory is architecturally significant for three reasons:

1. **Persistence across sessions** — Unlike a session-scoped LLM context, Ghost Memory persists between SPECTER runs on the same repository. Each time a repository is analyzed, the memory grows.

2. **Evidence grounding** — Every memory entry has a `source_ref` (commit SHA, issue URL, file path). This prevents the memory from becoming a collection of ungrounded LLM opinions.

3. **Anti-hallucination layer** — When the Repairer reads "this approach was previously rejected," it has a factual basis for avoiding that approach, reducing the risk of the LLM regenerating the same failed solution.

The PRD's distinction between **facts** (from code/history) and **hypotheses** (from LLM) is critical to Ghost Memory's reliability.

### 4.4 Security Model Understanding

SPECTER's security model is layered:

```
Layer 1 (Input): URL validation, GitHub URL allowlist
Layer 2 (Execution): Docker containers, no network, read-only mounts, resource limits
Layer 3 (Secrets): Token vault, token never reaches agents or LLM
Layer 4 (AI Output): Repository content in <context> tags, never as instructions
Layer 5 (Review): Independent Adversarial Reviewer catches injected content
Layer 6 (Human Gate): No remote changes without explicit human approval
Layer 7 (Audit): Immutable audit log of all actions
```

The critical principle: **repository content is treated as untrusted external data at every layer**.

---

## 5. Architectural Observations

### 5.1 The Python / Rust Split Rationale

The PRD states: "Python handles AI agent reasoning, Rust handles secure backend services and execution coordination."

This split is well-reasoned:
- Python is optimal for AI agent logic (rich ecosystem, LLM clients, data science tools)
- Rust is optimal for the security gateway (memory safety, no GC, type-safe SQL queries)
- The split also enforces the architectural rule that agents cannot directly access the GitHub token — they simply cannot, because the token is only in the Rust process

The split adds operational complexity (two languages, two build systems) but the security benefit justifies it.

### 5.2 Why Temporal for Workflow Durability

The repair pipeline has 5–7 sequential steps, each taking minutes, involving external systems, and potentially failing. Without Temporal:
- A crash between step 3 and 4 means starting over
- Implementing retry logic correctly in custom code is error-prone
- The approval gate (waiting for a human signal) would require a custom long-polling mechanism

Temporal solves all three problems natively. The tradeoff is operational complexity (Temporal server), but for a hackathon MVP, the Docker Compose setup is manageable.

### 5.3 Why Docker for Test Isolation

The PRD's security requirement is unambiguous: "Never execute repository code directly on the host." Docker containers provide OS-level isolation that is production-proven, well-documented, and operationally simple. The alternative (VMs, Firecracker) would add setup complexity inappropriate for the hackathon timeline.

The key risk (container escape via kernel exploit) is mitigated by the defense-in-depth approach: rootless Docker + capability dropping + seccomp + no network + resource limits.

### 5.4 Why pgvector for Ghost Memory

A separate vector database (Pinecone, Weaviate, Qdrant) would require:
- Another service to deploy and manage
- Cross-service synchronization (ensuring vector entries are consistent with relational data)
- Additional connection management

pgvector keeps everything in one database, which is appropriate for the MVP scope. The tradeoff is that PostgreSQL's vector search performance is slower than dedicated vector databases at very large scale (millions of entries). For a per-repository memory with hundreds to thousands of entries, pgvector is entirely sufficient.

### 5.5 Security Architecture Decisions

The most notable architectural decision is the **token vault pattern**: the GitHub token never leaves the Rust API service. The agent runtime (Python) cannot directly make GitHub write API calls. This means:

- Even if the agent runtime is compromised by a prompt injection attack, the attacker cannot directly create PRs or push branches
- The Rust API validates the approval request independently before using the token
- This is a strong defense against the most dangerous attack vector: compromised LLM output leading to unauthorized repository changes

---

## 6. Identified Ambiguities and Open Questions

The following 20 questions need answers before implementation begins. See `memory/BLOCKERS.md` for full details.

| ID | Question | Priority |
|---|---|---|
| Q-01 | Which Gemma model version is the default? (3:4b, 3:12b, 3:27b?) | P0 |
| Q-02 | What is the authentication mechanism for the API? (Anonymous JWT? GitHub OAuth?) | P0 |
| Q-03 | Are only public repositories supported, or also private repos? | P0 |
| Q-04 | What is the exact MCP tool list for each of the 6 agents? | P0 |
| Q-05 | How is the GitHub token stored if the server restarts? (User must re-enter? Persist encrypted?) | P0 |
| Q-06 | What is the embedding model? (nomic-embed-text? mxbai-embed-large? Gemma embed?) | P1 |
| Q-07 | Is the demo repository pre-selected, or chosen live? | P1 |
| Q-08 | What is the maximum repository size that should be supported? | P1 |
| Q-09 | Should Tree-sitter be used for all languages, or only the top 5? Which are the top 5? | P1 |
| Q-10 | How should the repair iteration limit (currently 3) be configured? | P1 |
| Q-11 | Should the Temporal Web UI be exposed in the production deployment? | P2 |
| Q-12 | How should the PR branch name be formatted? (`specter/{task_id}` vs `specter/{issue_number}/{slug}`) | P2 |
| Q-13 | Should SPECTER support repositories with no test suite? (Patch without test verification) | P2 |
| Q-14 | What is the expected latency SLA for the full pipeline end-to-end? | P2 |
| Q-15 | Is Temporal mTLS required for the hackathon MVP? | P2 |
| Q-16 | Should Ghost Memory entries be exportable (for repository maintainers to inspect)? | P2 |
| Q-17 | What happens if the LLM generates a patch that fails `git apply --check`? (Retry? Ask human?) | P1 |
| Q-18 | Should the Adversarial Reviewer use a different model or different model parameters? | P2 |
| Q-19 | Is there a plan for Windows development environment support? (Tree-sitter C bindings can be tricky) | P1 |
| Q-20 | What is the Hacktoberfest submission deadline? (This determines the MVP scope cutoff) | P0 |

---

## 7. Identified Risks

### 7.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Gemma 12B insufficient VRAM on demo hardware | High | Critical | Pre-test on demo machine; fallback to Gemma 4B |
| Tree-sitter Python bindings fail on target platform | Medium | High | Test early; have `pygments` as a fallback for language detection |
| Temporal Python SDK async/sync conflict | Medium | High | Write a minimal Temporal activity spike first |
| Temporal + PostgreSQL setup complexity | Medium | Medium | Use official `temporalio/auto-setup` Docker image |
| LLM generates invalid JSON despite instructions | High | Low | Retry with corrective prompt (max 3 times); pydantic validation |
| Container escape on demo machine | Low | Critical | Rootless Docker + defense-in-depth |
| React Flow performance with WebSocket message volume | Low | Low | Cap edge display at 100 messages; paginate |

### 7.2 Security Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Prompt injection via repository README | Medium | High | `<context>` delimiters + Adversarial Reviewer |
| GitHub token leaked to logs | Low | Critical | Token scrubber in log formatter |
| Test container network not disabled | Low | Critical | Automated test: verify `--network=none` in CI |
| Symlink in repository escaping workspace | Medium | High | Pre-mount symlink check |

### 7.3 Integration Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| GitHub API rate limits during demo | Medium | Medium | Use authenticated requests; implement backoff |
| Ollama model download time during demo | High | Medium | Pre-download model; use Ollama's model cache |
| Docker API version incompatibility | Low | Medium | Pin Docker API version in SDK calls |
| pgvector HNSW index recall insufficient | Low | Low | Tune `ef_construction`; fallback to flat index |

### 7.4 Timeline Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| 6 agents are too many for the hackathon timeline | High | High | Implement Archaeologist, Repairer, Reviewer first; others as stubs |
| Rust/Python integration (two language learning curves) | Medium | High | Dedicate a developer to Rust, a developer to Python |
| Demo repository selection late | Medium | Medium | Select demo repository by Day 3 of development |
| Hacktoberfest submission requirements unknown | Low | High | Read devrelay-knowledge skill for submission rules |

---

## 8. Initial Architecture Decisions Recommended

Based on the PRD analysis, the following key decisions should be made before a single line of code is written:

1. **Decide Gemma model default** — This determines the minimum hardware specification for the demo machine. Recommend `gemma3:12b` with `gemma3:4b` as the fallback if < 8 GB VRAM.

2. **Decide authentication model** — Anonymous JWT sessions (simpler, no login flow) vs. GitHub OAuth (better user identity, but more complex). For the MVP, anonymous JWT sessions with a GitHub token prompt is recommended.

3. **Decide monorepo vs. polyrepo** — Given the tight integration between services, a monorepo with separate `frontend/`, `api/`, `agents/` directories is recommended.

4. **Fix the embedding model** — Recommend `nomic-embed-text` (768 dimensions, fast, runs on Ollama, good semantic search quality). This cannot be changed mid-project without re-embedding all existing Ghost Memory entries.

5. **Fix the agent message format version** — Define v1 of the JSON message schema and version it explicitly. Schema changes break in-flight workflows.

6. **Decide on the demo repository** — Must be decided before the Test Engineer and Docker sandbox are implemented, because the test framework detection must be validated against the actual demo repo.

7. **Decide the repair iteration limit** — 3 iterations is recommended. Document this as a configuration parameter so it can be tuned.

8. **Define the MVP agent scope** — Recommend implementing 4 agents for MVP: Archaeologist, Repairer, Reviewer, Test Engineer (Coordinator as a workflow-level script, Investigator as a simplified version).

---

## 9. Recommended First Implementation Tasks

These are the five highest-priority tasks to begin immediately after planning is approved.

### SPECTER-001: Project Skeleton + Docker Compose (P0)

**Rationale:** All subsequent work requires a runnable environment. The skeleton establishes the monorepo structure, Docker Compose configuration, and verifies that all services can start and communicate.

**Scope:**
- Create directory structure: `frontend/`, `api/`, `agents/`, `db/`, `docs/`, `memory/`
- Docker Compose with: PostgreSQL + pgvector, Temporal, Ollama (empty), placeholder API and agent containers
- Verify: all services start, API health endpoint returns 200, Temporal worker connects

---

### SPECTER-002: Database Schema + Migrations (P0)

**Rationale:** The schema is the contract between all services. It must be defined before any service writes data.

**Scope:**
- All table definitions (repositories, tasks, agent_messages, ghost_memory, patches, reviews, test_results, approvals, audit_log)
- pgvector extension, HNSW index
- SQLx migration files
- Seed script for local development

---

### SPECTER-003: Rust API Foundation (P0)

**Rationale:** The API is the security boundary. All services depend on it.

**Scope:**
- Axum project setup, health endpoint
- JWT auth middleware
- Token vault (in-memory)
- `POST /api/v1/repositories` endpoint (URL validation, GitHub verification)
- `POST /api/v1/auth/session` endpoint
- Audit log writer
- Basic rate limiting middleware

---

### SPECTER-004: Temporal Workflow Skeleton + Repository Archaeologist (P0)

**Rationale:** The workflow engine and the first agent together validate the most complex part of the architecture. If the Temporal ↔ Python ↔ Ollama ↔ PostgreSQL chain works for the Archaeologist, all other agents follow the same pattern.

**Scope:**
- Temporal worker setup (Python)
- `RepositoryMaintenanceWorkflow` skeleton (stages with stub activities)
- `SpectreAgent` base class with Ollama client and Ghost Memory read/write
- `clone_repository` activity
- `run_archaeologist` activity (Tree-sitter + Git log + LLM + memory write)
- `ghost_memory` embedding pipeline (nomic-embed-text via Ollama)

---

### SPECTER-005: Frontend Repository Dashboard + WebSocket (P0)

**Rationale:** The frontend is needed for the demo and for validating the real-time agent communication display.

**Scope:**
- Next.js project setup with TypeScript, Tailwind, shadcn/ui
- Repository input form (URL + token)
- Repository dashboard page
- React Flow agent graph (nodes for 6 agents, edges from agent messages)
- WebSocket connection to API
- Live log stream display
- Repository Context Report display

---
