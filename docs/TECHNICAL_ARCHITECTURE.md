# SPECTER — Technical Architecture

> **Document Status:** Planning Phase — Not Yet Implemented  
> **Version:** 0.1.0  
> **Last Updated:** 2026-10-31  
> **Challenge:** Hacktoberfest 2026 — Ghost in the Machine

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Component Specifications](#2-component-specifications)
3. [Data Flow Diagrams](#3-data-flow-diagrams)
4. [Database Schema](#4-database-schema)
5. [API Endpoints Reference](#5-api-endpoints-reference)
6. [Deployment Architecture](#6-deployment-architecture)

---

## 1. System Overview

SPECTER is a multi-service system composed of six architectural layers. Each layer has a clearly defined responsibility boundary:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SPECTER SYSTEM BOUNDARY                             │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                       FRONTEND (Next.js 14+)                        │   │
│  │   React Flow Graph  │  shadcn/ui  │  WebSocket Client  │  SSE Feed  │   │
│  └─────────────────────────────────┬────────────────────────────────────┘   │
│                                    │ HTTPS / WebSocket                      │
│  ┌─────────────────────────────────▼────────────────────────────────────┐   │
│  │                    API GATEWAY  (Rust / Axum)                        │   │
│  │  REST Routes │ WebSocket Hub │ Auth Middleware │ Rate Limiter        │   │
│  │  GitHub Token Vault │ Audit Logger │ Request Validator               │   │
│  └──────┬───────────────────┬──────────────────────┬────────────────────┘   │
│         │ SQL               │ Temporal SDK          │ Docker API             │
│         │                   │                       │                        │
│  ┌──────▼───────┐  ┌────────▼──────────┐  ┌────────▼───────────────────┐   │
│  │  PostgreSQL  │  │ Temporal Server   │  │   Docker Daemon (sandboxed) │   │
│  │  + pgvector  │  │ (Workflow Engine) │  │   Test Containers           │   │
│  └──────────────┘  └────────┬──────────┘  └─────────────────────────────┘   │
│                             │ Activity Tasks                                 │
│  ┌──────────────────────────▼────────────────────────────────────────────┐   │
│  │                   AGENT RUNTIME  (Python 3.12+)                       │   │
│  │                                                                       │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────────┐ │   │
│  │  │  Archaeologist│  │Issue Invest.  │  │   Ghost Repairer          │ │   │
│  │  └───────────────┘  └───────────────┘  └───────────────────────────┘ │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────────┐ │   │
│  │  │  Adv. Reviewer│  │ Test Engineer │  │  Resurrection Coordinator │ │   │
│  │  └───────────────┘  └───────────────┘  └───────────────────────────┘ │   │
│  │                                                                       │   │
│  │  MCP Tool Layer │ Ollama Client │ Tree-sitter Parser │ Git CLI       │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                  EXTERNAL INTEGRATIONS                               │   │
│  │         GitHub API  │  Ollama (local)  │  OpenTelemetry Collector   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Service Boundaries Summary

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Next.js 14+, TypeScript, React Flow | User interface, agent visualization |
| API Gateway | Rust, Axum | REST API, auth, token vault, audit |
| Agent Runtime | Python 3.12+, asyncio | AI agent execution, LLM calls |
| Workflow Engine | Temporal | Durable execution, retries, state |
| Data Store | PostgreSQL 16 + pgvector | Persistence, Ghost Memory |
| Test Sandbox | Docker (rootless) | Isolated test execution |

---

## 2. Component Specifications

### 2.1 Frontend Architecture (Next.js)

**Technology:** Next.js 14+ with App Router, TypeScript, Tailwind CSS, shadcn/ui, React Flow, Tanstack Query, Zustand

**Rationale:** Next.js provides server-side rendering for initial page load performance, seamless API routes for BFF (Backend for Frontend) patterns, and a strong ecosystem. React Flow is the best-in-class library for rendering directed agent communication graphs.

**Responsibilities:**
- Render the repository onboarding form (URL input + GitHub token input)
- Display live agent activity graph via React Flow nodes and edges
- Stream agent log output via Server-Sent Events (SSE)
- Show diff viewer for proposed patches (using `react-diff-view`)
- Present the human approval gate before PR creation
- Display Ghost Memory entries per repository
- Render the maintenance report in structured Markdown

**Key UI Pages:**

```
/                          → Landing / Repository Input
/repos/[id]                → Repository Dashboard
/repos/[id]/tasks/[taskId] → Task Detail + Agent Graph
/repos/[id]/memory         → Ghost Memory Browser
/repos/[id]/history        → Audit Log
/approval/[taskId]         → Human Approval Gate
```

**WebSocket Connection:**
- Connect to `ws://api/ws/tasks/{task_id}` for live agent messages
- Receive `AgentMessage` events and render them as graph edges
- Receive `LogLine` events and stream to terminal view

**State Management:**
- Zustand for global repository/task state
- Tanstack Query for server state (REST calls, caching, invalidation)

**Build Output:** Static export or standard Next.js Node.js server (to be decided — see BLOCKERS.md BLK-007)

---

### 2.2 Rust / Axum Backend API

**Technology:** Rust (stable), Axum 0.7+, Tower middleware, SQLx (async PostgreSQL), Tokio async runtime, serde + serde_json, jsonwebtoken

**Rationale:** Rust provides memory safety without a garbage collector, making it well-suited for the security-sensitive gateway role. Axum's Tower-based middleware composes cleanly. SQLx provides compile-time-verified SQL queries.

**Responsibilities:**
- Expose the REST API consumed by the frontend
- Manage WebSocket connections and fan out agent messages to subscribers
- Validate and store GitHub tokens securely (never logging them)
- Issue and validate session JWTs
- Enforce rate limits per user session and per GitHub repository URL
- Dispatch workflow start/cancel commands to Temporal
- Write all agent actions to the immutable audit log
- Proxy Docker container status without exposing host socket to agents

**Middleware Stack (applied in order):**

```
Request → TraceLayer (OpenTelemetry) → CorsLayer → AuthLayer (JWT) 
       → RateLimitLayer → RequestIdLayer → Handler → AuditLogLayer
       → Response
```

**Key Internal Modules:**
- `auth`: JWT issuance and verification
- `vault`: Encrypted in-memory store for GitHub tokens (per session)
- `github`: GitHub API client (read-only until approval)
- `temporal_client`: gRPC client to Temporal Frontend service
- `docker_proxy`: Docker API client for container status queries
- `ws_hub`: WebSocket broadcast hub keyed by task ID
- `audit`: Append-only audit log writer to PostgreSQL

---

### 2.3 Python Agent Runtime

**Technology:** Python 3.12+, asyncio, Temporalio Python SDK, `ollama` Python client, `tree_sitter` Python bindings, `pygithub` or `httpx` for GitHub, `pydantic` for schema validation, `structlog` for structured logging

**Rationale:** Python has the richest ecosystem for AI agent tooling, LLM clients, and code analysis. The Temporalio Python SDK allows agents to run as Temporal Activities with native async support.

**Agent Base Class:**

```python
class SpectreAgent(ABC):
    """All agents inherit from this base class."""
    agent_id: str
    task_id: str
    db: AsyncConnection
    ollama_client: OllamaClient
    memory_store: GhostMemoryStore
    message_bus: AgentMessageBus

    async def run(self, context: AgentContext) -> AgentResult:
        """Entry point — implemented by each agent."""
        ...

    async def emit_message(self, to: str, msg_type: str, payload: dict) -> None:
        """Send a structured A2A message, persisted and broadcast via WebSocket."""
        ...

    async def read_memory(self, query: str, category: str) -> list[MemoryEntry]:
        """Vector similarity search against Ghost Memory for this repository."""
        ...

    async def write_memory(self, entry: MemoryEntry) -> None:
        """Persist a new Ghost Memory entry with source reference."""
        ...
```

**MCP Integration:**
- Each agent exposes its tool set as an MCP server
- The Resurrection Coordinator acts as an MCP client to invoke agent tools
- Tools are registered at startup and validated against a JSON Schema registry

**Ollama Client:**
- Uses the `/api/generate` and `/api/chat` endpoints
- Model name is configurable via environment variable (`SPECTER_LLM_MODEL`, default `gemma3:12b`)
- All prompts are constructed programmatically — repository content inserted as `<context>` blocks, never as system instructions
- Token budgets enforced per agent (configurable limits)

---

### 2.4 Temporal Workflow Engine

**Technology:** Temporal Server (open-source), Temporal Python SDK, Temporal Web UI

**Rationale:** Temporal provides durable execution — if any worker crashes, the workflow resumes from the last checkpoint. This directly implements FR-14 (failure recovery). It also provides built-in retry logic, timeout enforcement, and a visual workflow history.

**Main Workflow: `RepositoryMaintenanceWorkflow`**

```python
@workflow.defn
class RepositoryMaintenanceWorkflow:
    """Top-level workflow executed per maintenance task."""

    @workflow.run
    async def run(self, input: MaintenanceInput) -> MaintenanceResult:
        # Activity 1: Clone repository into isolated workspace
        workspace = await workflow.execute_activity(
            clone_repository, input.repo_url,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        # Activity 2: Run Repository Archaeologist
        archaeology = await workflow.execute_activity(
            run_archaeologist, workspace,
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=RetryPolicy(maximum_attempts=2)
        )
        # Activity 3: Issue Investigation
        investigation = await workflow.execute_activity(
            run_issue_investigator, (workspace, input.issue_number),
            start_to_close_timeout=timedelta(minutes=20),
        )
        # Activity 4: Ghost Repairer
        patch = await workflow.execute_activity(
            run_ghost_repairer, (workspace, investigation),
            start_to_close_timeout=timedelta(minutes=20),
        )
        # Activity 5: Adversarial Review (may loop back to repair)
        review = await workflow.execute_activity(
            run_adversarial_reviewer, patch,
            start_to_close_timeout=timedelta(minutes=15),
        )
        if review.verdict == "rejected":
            patch = await workflow.execute_activity(
                run_ghost_repairer, (workspace, review.corrections),
                start_to_close_timeout=timedelta(minutes=20),
            )
        # Activity 6: Test Execution
        test_result = await workflow.execute_activity(
            run_test_engineer, (workspace, patch),
            start_to_close_timeout=timedelta(minutes=30),
        )
        # Activity 7: Human approval gate (signal-based wait)
        await workflow.wait_condition(lambda: self._approved or self._rejected)
        if self._approved:
            pr = await workflow.execute_activity(
                create_pull_request, (workspace, patch),
                start_to_close_timeout=timedelta(minutes=5),
            )
        return MaintenanceResult(patch=patch, review=review, tests=test_result)
```

**Retry Policies:**

| Activity | Max Attempts | Timeout | Backoff |
|---|---|---|---|
| clone_repository | 3 | 5 min | Exponential |
| run_archaeologist | 2 | 30 min | Linear |
| run_issue_investigator | 2 | 20 min | Linear |
| run_ghost_repairer | 3 | 20 min | Exponential |
| run_adversarial_reviewer | 2 | 15 min | Linear |
| run_test_engineer | 2 | 30 min | Linear |
| create_pull_request | 3 | 5 min | Exponential |

**Signals:**
- `approve_task` — sent by Rust API on human approval
- `reject_task` — sent by Rust API on human rejection

**Queries:**
- `get_current_stage` — returns the current workflow stage name

---

### 2.5 PostgreSQL Schema Overview

**Technology:** PostgreSQL 16, pgvector extension

**Rationale:** A single relational database simplifies operations. pgvector adds vector search within the same transaction boundary as other data, avoiding synchronization problems between a separate vector store and the application database.

See **Section 4** for full table definitions.

**Key Tables:**
- `repositories` — indexed repository metadata
- `tasks` — maintenance task records linked to repositories and issues
- `agent_messages` — all A2A messages (append-only)
- `ghost_memory` — vector-embedded memory entries per repository
- `audit_log` — immutable action log with actor, action, timestamp
- `patches` — proposed code patches linked to tasks
- `test_results` — test execution results per patch
- `workflow_signals` — approval/rejection records

---

### 2.6 pgvector Integration (Ghost Memory)

**Technology:** pgvector 0.7+, embedding model: `nomic-embed-text` via Ollama (768-dimensional embeddings)

**Rationale:** Ghost Memory is the project's signature feature. Storing embeddings in pgvector means vector similarity queries run inside the same database as all other data, eliminating the need for a separate Pinecone/Weaviate instance.

**Embedding Pipeline:**

```
Memory Entry Text
      ↓
Ollama /api/embeddings (nomic-embed-text)
      ↓
768-dimensional float vector
      ↓
INSERT INTO ghost_memory (repo_id, category, content, embedding, source_ref, ...)
```

**Similarity Search Query:**

```sql
SELECT id, category, content, source_ref, confidence,
       1 - (embedding <=> query_embedding) AS similarity
FROM ghost_memory
WHERE repo_id = $1
  AND category = ANY($2)
ORDER BY embedding <=> query_embedding
LIMIT 10;
```

**Index:** `HNSW` index on `embedding` column for approximate nearest-neighbor search:

```sql
CREATE INDEX ghost_memory_embedding_hnsw_idx
ON ghost_memory USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

---

### 2.7 Docker Isolation Layer

**Technology:** Docker Engine (rootless mode preferred), Docker SDK for Python (`docker` package), custom `Dockerfile.sandbox` base image

**Rationale:** Docker containers provide OS-level isolation without VM overhead. Rootless Docker prevents container processes from mapping to root on the host. Each test run gets a fresh, disposable container.

**Container Lifecycle:**

```
1. Agent requests test execution
2. Rust backend calls Docker API: create container
3. Container created from pre-built sandbox image
   - Base: ubuntu:24.04 or language-specific (python:3.12-slim, node:22-slim, etc.)
   - Repository workspace bind-mounted READ-ONLY to /workspace
   - Writable tmpfs at /tmp only
4. Container started with resource limits applied
5. Test command executed (e.g., `pytest`, `cargo test`, `npm test`)
6. stdout/stderr streamed back via Docker logs API
7. Exit code captured
8. Container stopped and removed (always, even on failure)
9. Result returned to agent
```

**Resource Limits (per container):**

| Limit | Default Value |
|---|---|
| CPU cores | 2 |
| Memory | 2 GB |
| Wall-clock timeout | 10 minutes |
| Disk (tmpfs) | 512 MB |
| Process count (pids) | 256 |
| Network | Disabled (--network=none) |

**Security Constraints:**
- `--network=none` — no outbound or inbound network access
- `--read-only` root filesystem except `/tmp` (tmpfs)
- `--no-new-privileges` — prevents privilege escalation
- `--cap-drop=ALL` — all Linux capabilities dropped
- No host path mounts except `/workspace` (read-only, checked for symlink attacks)
- No environment variables from the host injected into containers

---

### 2.8 GitHub Integration

**Technology:** GitHub REST API v3 (via `httpx` async client), GitHub Personal Access Token (PAT)

**Responsibilities:**
- Validate repository exists and is public (FR-01)
- Fetch issue list and issue detail (FR-04)
- Create a branch on the repository (FR-13, post-approval only)
- Open a Pull Request with the generated patch and maintenance report (FR-13)

**Token Handling:**
- GitHub token accepted from the user at session start via the frontend
- Stored in the Rust `vault` module (encrypted in memory, not persisted to disk)
- Token never passed to Ollama or any agent prompt
- Token never written to logs
- Token used only by the Rust API service for GitHub API calls
- Token transmitted to frontend over HTTPS only (never in WebSocket messages)

**API Operations:**

| Operation | Method | Endpoint | Auth Required |
|---|---|---|---|
| Validate repo | GET | /repos/{owner}/{repo} | Optional (rate limit) |
| List issues | GET | /repos/{owner}/{repo}/issues | Yes |
| Get issue | GET | /repos/{owner}/{repo}/issues/{number} | Yes |
| Create branch | POST | /repos/{owner}/{repo}/git/refs | Yes |
| Create PR | POST | /repos/{owner}/{repo}/pulls | Yes |

**Rate Limiting:** The Rust API client respects GitHub's `X-RateLimit-Remaining` header and implements exponential backoff on 429 responses.

---

### 2.9 Ollama / Gemma LLM Integration

**Technology:** Ollama local inference server, Gemma 3 model family (12B parameter default)

**Rationale:** Local inference via Ollama ensures no repository content, code, or issue text is sent to external APIs. This is a hard security requirement. Gemma is Google's open-weight model family with strong coding ability.

**Model Selection:**

| Model | VRAM Required | Use Case |
|---|---|---|
| `gemma3:4b` | ~4 GB | Low-resource environments, demo |
| `gemma3:12b` | ~10 GB | Default (recommended for accuracy) |
| `gemma3:27b` | ~20 GB | High-accuracy production mode |

**Prompt Architecture:**

Each agent constructs prompts following this structure:

```
[SYSTEM ROLE DEFINITION — fixed, not from repository]
[TASK DESCRIPTION — constructed by agent code]
<context>
  [REPOSITORY DATA — treated as untrusted external data]
</context>
[STRUCTURED OUTPUT INSTRUCTIONS — JSON schema for response]
```

Repository README, code, comments, and issue text are always placed inside `<context>` tags and are never placed in the system prompt section.

**Response Parsing:**
- All agents request JSON-format responses
- Responses are parsed via Pydantic models
- Invalid JSON triggers a retry (up to 3 times) with a corrective prompt
- Hallucinated file paths are checked against the actual workspace

---

### 2.10 Tree-sitter Code Parsing

**Technology:** Tree-sitter (Rust core), `tree_sitter` Python bindings, language grammars for Python, JavaScript, TypeScript, Rust, Go, Java, Ruby, C, C++

**Rationale:** Tree-sitter produces concrete syntax trees (CSTs) for source code without executing it. This enables the Repository Archaeologist to extract function signatures, class hierarchies, import graphs, and call relationships — all without executing any repository code.

**Analysis Capabilities:**
- Language detection (by file extension + content heuristic)
- Function/method signature extraction
- Class and module hierarchy mapping
- Import/dependency graph construction
- Symbol reference tracking (where is this function called?)
- Diff-level AST comparison (did this patch change the public API?)

**Usage in Agents:**

| Agent | Tree-sitter Usage |
|---|---|
| Repository Archaeologist | Full codebase symbol map |
| Issue Investigator | Identify affected functions |
| Ghost Repairer | Validate patch syntax correctness |
| Adversarial Reviewer | Check patch does not change public API unexpectedly |
| Test Engineer | Identify test functions and test framework |

---

### 2.11 Agent-to-Agent Communication Layer

**Technology:** PostgreSQL `agent_messages` table as persistent message bus, Rust WebSocket hub for real-time fan-out

**Message Schema (Pydantic):**

```python
class AgentMessage(BaseModel):
    message_id: UUID
    task_id: UUID
    from_agent: AgentId          # enum: archaeologist | investigator | repairer | reviewer | engineer | coordinator
    to_agent: AgentId
    message_type: MessageType    # enum: see below
    payload: dict                # validated against per-type JSON schema
    evidence_refs: list[str]     # file paths, commit SHAs, issue URLs
    timestamp: datetime
    status: MessageStatus        # enum: pending | delivered | processed | failed

class MessageType(str, Enum):
    REPOSITORY_CONTEXT = "repository_context"
    REPAIR_SPECIFICATION = "repair_specification"
    PROPOSED_PATCH = "proposed_patch"
    REVIEW_VERDICT = "review_verdict"
    TEST_RESULT = "test_result"
    CORRECTION_REQUEST = "correction_request"
    APPROVAL_REQUEST = "approval_request"
    COMPLETION = "completion"
```

**Delivery Guarantees:**
- Messages are written to `agent_messages` before any agent processes them
- The Resurrection Coordinator reads unprocessed messages on startup (crash recovery)
- Messages are immutable after creation (append-only)
- Each message has a `status` field updated as it is processed

**Validation:**
- Each `message_type` has a corresponding Pydantic model for its `payload`
- The Coordinator validates the payload schema before forwarding to the next agent
- Schema validation failures are logged as `SCHEMA_VALIDATION_ERROR` audit events

---

### 2.12 Observability Stack

**Technology:** OpenTelemetry Python SDK, OpenTelemetry Rust SDK (for Axum), Jaeger (trace storage, local), Prometheus (metrics), Grafana (dashboards), `structlog` (Python structured logs)

**Traces:** Every agent run, LLM call, Docker operation, and GitHub API call is wrapped in an OpenTelemetry span. Traces are exported to Jaeger via OTLP.

**Metrics (Prometheus):**

| Metric | Type | Description |
|---|---|---|
| `specter_tasks_total` | Counter | Total maintenance tasks started |
| `specter_tasks_completed` | Counter | Tasks completed successfully |
| `specter_agent_duration_seconds` | Histogram | Per-agent execution time |
| `specter_llm_tokens_total` | Counter | LLM tokens consumed per model |
| `specter_docker_containers_active` | Gauge | Running test containers |
| `specter_patches_reviewed_total` | Counter | Patches reviewed |
| `specter_patches_accepted_ratio` | Gauge | Fraction of patches accepted |

**Structured Log Fields (all services):**

```json
{
  "timestamp": "2026-10-31T12:00:00Z",
  "level": "INFO",
  "service": "specter-agent-runtime",
  "task_id": "uuid",
  "agent": "ghost_repairer",
  "trace_id": "otel-trace-id",
  "span_id": "otel-span-id",
  "message": "Patch generated successfully",
  "patch_lines_added": 12,
  "patch_lines_removed": 3
}
```

---

## 3. Data Flow Diagrams

### 3.1 Repository Ingestion Flow

```
User (Browser)
    │
    │ POST /api/repositories { url, github_token }
    ▼
Rust API (validate URL format, store token in vault)
    │
    │ INSERT INTO repositories
    │ Temporal: StartWorkflow(RepositoryMaintenanceWorkflow)
    ▼
Temporal Worker (Python)
    │
    │ Activity: clone_repository
    ▼
Git CLI (git clone --depth=50 <url> /workspace/<repo_id>)
    │
    │ workspace directory created
    ▼
Activity: run_archaeologist
    │
    ├── Tree-sitter: parse all source files → symbol map
    ├── Git log: extract commit history (last 200 commits)
    ├── README, LICENSE, config files read
    ├── Ollama: generate Repository Context Report
    └── Ghost Memory: write initial memory entries
    │
    │ AgentMessage(REPOSITORY_CONTEXT) → agent_messages table
    ▼
Rust API broadcasts AgentMessage via WebSocket to frontend
    │
    ▼
Frontend renders Archaeologist node as "complete" in React Flow graph
```

### 3.2 Issue Investigation Flow

```
User selects issue from list
    │
    │ POST /api/tasks { repo_id, issue_number }
    ▼
Rust API (fetch issue from GitHub API, store in task record)
    │
    │ Temporal: Signal workflow with issue_selected
    ▼
Activity: run_issue_investigator
    │
    ├── Read Ghost Memory (query: issue keywords)
    ├── Tree-sitter: locate affected symbols
    ├── Git log: find commits touching affected files
    ├── Ollama: analyze root cause
    └── Generate Investigation Report + Repair Specification
    │
    │ AgentMessage(REPAIR_SPECIFICATION) → agent_messages table
    ▼
Activity: run_ghost_repairer
```

### 3.3 Repair and Review Flow

```
Ghost Repairer receives REPAIR_SPECIFICATION
    │
    ├── Read Ghost Memory (rejected approaches, previous fixes)
    ├── Tree-sitter: validate affected file AST
    ├── Ollama: generate minimal patch
    └── Write patch to /workspace/<repo_id>/specter.patch
    │
    │ AgentMessage(PROPOSED_PATCH) → agent_messages table
    ▼
Adversarial Reviewer receives PROPOSED_PATCH
    │
    ├── Read patch independently (no repairer context passed)
    ├── Tree-sitter: verify AST validity after applying patch
    ├── Ghost Memory: check for known rejected approaches
    ├── Ollama: independent critique (separate LLM call)
    └── Generate Review Verdict
    │
    │ If REJECTED → AgentMessage(CORRECTION_REQUEST)
    │                  └─→ Ghost Repairer (retry, max 3 times)
    │ If ACCEPTED → AgentMessage(REVIEW_VERDICT) → Test Engineer
    ▼
Activity: run_test_engineer
```

### 3.4 Test Execution Flow

```
Test Engineer receives REVIEW_VERDICT (accepted patch)
    │
    ├── Detect test framework (pytest, jest, cargo test, etc.)
    ├── Apply patch to workspace copy
    │
    │ Docker API: create container
    ▼
Docker Container (isolated, --network=none)
    │
    ├── /workspace bind-mounted READ-ONLY
    ├── Copy patched files to /tmp/patched_workspace
    ├── Run: <test_command> 2>&1
    └── Exit code + stdout + stderr captured
    │
    │ Container stopped and removed
    ▼
Test Engineer
    │
    ├── Parse test output (pass/fail counts, error messages)
    ├── Write test result to ghost_memory (verified patch or failed attempt)
    └── AgentMessage(TEST_RESULT) → agent_messages table
    │
    ▼
Resurrection Coordinator: request human approval
```

### 3.5 PR Creation Flow

```
Human views Approval Gate (frontend)
    │  Shows: patch diff, review verdict, test results
    │
    │ POST /api/tasks/{task_id}/approve { confirmed: true }
    ▼
Rust API validates approval, writes to audit_log
    │
    │ Temporal: Signal workflow with approve_task
    ▼
Activity: create_pull_request
    │
    ├── GitHub API: create branch specter/{task_id}
    ├── GitHub API: push commit with patch
    ├── GitHub API: create PR with maintenance report as body
    └── PR URL stored in task record
    │
    ▼
Frontend shows PR link
```

---

## 4. Database Schema

### 4.1 Full Table Definitions

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "vector";    -- pgvector

-- ============================================================
-- ENUM TYPES
-- ============================================================

CREATE TYPE task_status AS ENUM (
    'pending', 'archaeology', 'investigating', 'repairing',
    'reviewing', 'testing', 'awaiting_approval', 'creating_pr',
    'completed', 'failed', 'cancelled'
);

CREATE TYPE agent_id AS ENUM (
    'archaeologist', 'investigator', 'repairer',
    'reviewer', 'engineer', 'coordinator'
);

CREATE TYPE message_type AS ENUM (
    'repository_context', 'repair_specification', 'proposed_patch',
    'review_verdict', 'test_result', 'correction_request',
    'approval_request', 'completion'
);

CREATE TYPE message_status AS ENUM ('pending', 'delivered', 'processed', 'failed');

CREATE TYPE memory_category AS ENUM (
    'architectural_decision', 'historical_bug_fix', 'rejected_approach',
    'known_broken_dependency', 'unresolved_issue', 'investigation_report',
    'verified_patch'
);

CREATE TYPE memory_confidence AS ENUM ('fact', 'hypothesis', 'speculation');

CREATE TYPE review_verdict AS ENUM ('accepted', 'rejected', 'conditional');

-- ============================================================
-- CORE TABLES
-- ============================================================

CREATE TABLE repositories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    github_url      TEXT NOT NULL,
    owner           TEXT NOT NULL,
    repo_name       TEXT NOT NULL,
    default_branch  TEXT NOT NULL DEFAULT 'main',
    description     TEXT,
    language        TEXT,
    stars           INT,
    workspace_path  TEXT,                    -- host path to cloned workspace
    cloned_at       TIMESTAMPTZ,
    last_analyzed   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT repositories_url_unique UNIQUE (github_url)
);

CREATE TABLE tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repo_id         UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    issue_number    INT,                     -- NULL if not issue-driven
    issue_title     TEXT,
    issue_body      TEXT,
    status          task_status NOT NULL DEFAULT 'pending',
    temporal_workflow_id TEXT,               -- Temporal workflow run ID
    current_stage   TEXT,
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

CREATE TABLE agent_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id         UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    from_agent      agent_id NOT NULL,
    to_agent        agent_id NOT NULL,
    message_type    message_type NOT NULL,
    payload         JSONB NOT NULL,
    evidence_refs   TEXT[] NOT NULL DEFAULT '{}',
    status          message_status NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at    TIMESTAMPTZ
);

CREATE TABLE ghost_memory (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repo_id         UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    task_id         UUID REFERENCES tasks(id) ON DELETE SET NULL,
    category        memory_category NOT NULL,
    content         TEXT NOT NULL,
    embedding       vector(768),             -- nomic-embed-text embeddings
    source_ref      TEXT,                    -- commit SHA, issue URL, file path, etc.
    confidence      memory_confidence NOT NULL DEFAULT 'hypothesis',
    is_superseded   BOOLEAN NOT NULL DEFAULT FALSE,
    superseded_by   UUID REFERENCES ghost_memory(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by      agent_id NOT NULL
);

CREATE TABLE patches (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id         UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    patch_content   TEXT NOT NULL,           -- unified diff format
    patch_iteration INT NOT NULL DEFAULT 1,  -- increments on each repairer cycle
    affected_files  TEXT[] NOT NULL DEFAULT '{}',
    lines_added     INT NOT NULL DEFAULT 0,
    lines_removed   INT NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE reviews (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patch_id        UUID NOT NULL REFERENCES patches(id) ON DELETE CASCADE,
    task_id         UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    verdict         review_verdict NOT NULL,
    critique        TEXT NOT NULL,
    security_issues TEXT[],
    regression_risks TEXT[],
    corrections_requested TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE test_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patch_id        UUID NOT NULL REFERENCES patches(id) ON DELETE CASCADE,
    task_id         UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    framework       TEXT,                    -- pytest, jest, cargo-test, etc.
    passed          BOOLEAN,
    total_tests     INT,
    passed_tests    INT,
    failed_tests    INT,
    error_tests     INT,
    raw_output      TEXT,
    exit_code       INT,
    duration_seconds FLOAT,
    container_image TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE approvals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id         UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    approved        BOOLEAN NOT NULL,
    approver_session TEXT NOT NULL,          -- session ID (not user identity)
    pr_url          TEXT,                    -- populated after PR creation
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_log (
    id              BIGSERIAL PRIMARY KEY,   -- sequential for ordering
    task_id         UUID REFERENCES tasks(id),
    repo_id         UUID REFERENCES repositories(id),
    actor           TEXT NOT NULL,           -- 'user:{session}' or 'agent:{name}'
    action          TEXT NOT NULL,
    details         JSONB NOT NULL DEFAULT '{}',
    ip_address      INET,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
    -- NO DELETE, NO UPDATE — append-only
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX tasks_repo_id_idx ON tasks(repo_id);
CREATE INDEX tasks_status_idx ON tasks(status);
CREATE INDEX agent_messages_task_id_idx ON agent_messages(task_id);
CREATE INDEX agent_messages_status_idx ON agent_messages(status);
CREATE INDEX ghost_memory_repo_id_idx ON ghost_memory(repo_id);
CREATE INDEX ghost_memory_category_idx ON ghost_memory(category);
CREATE INDEX ghost_memory_embedding_hnsw_idx ON ghost_memory
    USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX patches_task_id_idx ON patches(task_id);
CREATE INDEX audit_log_task_id_idx ON audit_log(task_id);
CREATE INDEX audit_log_created_at_idx ON audit_log(created_at);
```

---

## 5. API Endpoints Reference

All endpoints use base path `/api/v1`. All authenticated endpoints require `Authorization: Bearer <jwt>` header.

### Repository Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/repositories` | Yes | Register a new repository for analysis |
| `GET` | `/repositories` | Yes | List all repositories for this session |
| `GET` | `/repositories/{repo_id}` | Yes | Get repository detail and current status |
| `DELETE` | `/repositories/{repo_id}` | Yes | Remove repository (deletes workspace) |

**POST /repositories — Request:**
```json
{
  "github_url": "https://github.com/owner/repo",
  "github_token": "ghp_xxxxxxxxxxxx"
}
```
**POST /repositories — Response (201):**
```json
{
  "id": "uuid",
  "github_url": "https://github.com/owner/repo",
  "owner": "owner",
  "repo_name": "repo",
  "status": "pending",
  "created_at": "2026-10-31T12:00:00Z"
}
```

### Task Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/repositories/{repo_id}/tasks` | Yes | Start a new maintenance task |
| `GET` | `/repositories/{repo_id}/tasks` | Yes | List tasks for a repository |
| `GET` | `/tasks/{task_id}` | Yes | Get task detail + current stage |
| `GET` | `/tasks/{task_id}/messages` | Yes | Get all agent messages for a task |
| `GET` | `/tasks/{task_id}/patch` | Yes | Get current proposed patch |
| `GET` | `/tasks/{task_id}/review` | Yes | Get review verdict |
| `GET` | `/tasks/{task_id}/test-result` | Yes | Get test result |
| `POST` | `/tasks/{task_id}/approve` | Yes | Approve task and trigger PR creation |
| `POST` | `/tasks/{task_id}/reject` | Yes | Reject proposed patch |
| `POST` | `/tasks/{task_id}/cancel` | Yes | Cancel an in-progress task |

**POST /tasks/{task_id}/approve — Request:**
```json
{
  "confirmed": true,
  "pr_title": "fix: correct null handling in parser.ts",
  "pr_body_append": "Optional human note to append to PR body"
}
```

### Memory Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/repositories/{repo_id}/memory` | Yes | Query Ghost Memory |
| `GET` | `/repositories/{repo_id}/memory/{entry_id}` | Yes | Get specific memory entry |

**GET /memory — Query params:** `?category=architectural_decision&query=null+handling&limit=20`

### Issues Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/repositories/{repo_id}/issues` | Yes | Fetch issues from GitHub (proxied) |
| `GET` | `/repositories/{repo_id}/issues/{number}` | Yes | Fetch specific issue detail |

### Audit Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/repositories/{repo_id}/audit` | Yes | Get audit log for repository |
| `GET` | `/tasks/{task_id}/audit` | Yes | Get audit log for task |

### Auth Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/session` | No | Create anonymous session, returns JWT |
| `DELETE` | `/auth/session` | Yes | Revoke session and purge token from vault |

### WebSocket

| Path | Description |
|---|---|
| `ws://host/ws/tasks/{task_id}` | Live agent message stream for a task |

WebSocket message format:
```json
{
  "event": "agent_message",
  "data": { /* AgentMessage object */ }
}
```

---

## 6. Deployment Architecture

### 6.1 Docker Compose Services

```yaml
# docker-compose.yml (development)
services:

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8080/api/v1
      - NEXT_PUBLIC_WS_URL=ws://localhost:8080/ws
    depends_on:
      - api

  api:
    build: ./api
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://specter:specter@postgres:5432/specter
      - TEMPORAL_HOST=temporal:7233
      - JWT_SECRET=${JWT_SECRET}
      - DOCKER_SOCKET=/var/run/docker.sock
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - specter_workspaces:/workspaces
    depends_on:
      postgres:
        condition: service_healthy
      temporal:
        condition: service_started

  agent-worker:
    build: ./agents
    environment:
      - DATABASE_URL=postgresql://specter:specter@postgres:5432/specter
      - TEMPORAL_HOST=temporal:7233
      - OLLAMA_HOST=http://ollama:11434
      - WORKSPACE_ROOT=/workspaces
      - SPECTER_LLM_MODEL=gemma3:12b
      - SPECTER_EMBED_MODEL=nomic-embed-text
    volumes:
      - specter_workspaces:/workspaces
    depends_on:
      - postgres
      - temporal
      - ollama

  postgres:
    image: pgvector/pgvector:pg16
    environment:
      - POSTGRES_USER=specter
      - POSTGRES_PASSWORD=specter
      - POSTGRES_DB=specter
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./db/migrations:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U specter"]
      interval: 5s
      timeout: 5s
      retries: 5

  temporal:
    image: temporalio/auto-setup:latest
    ports:
      - "7233:7233"
      - "8233:8233"    # Temporal Web UI
    environment:
      - DB=postgresql
      - DB_PORT=5432
      - POSTGRES_USER=specter
      - POSTGRES_PWD=specter
      - POSTGRES_SEEDS=postgres
    depends_on:
      postgres:
        condition: service_healthy

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    volumes:
      - ./observability/otel-config.yaml:/etc/otel/config.yaml
    ports:
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./observability/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

volumes:
  postgres_data:
  ollama_models:
  specter_workspaces:
```

### 6.2 Environment Variables Reference

| Variable | Service | Description | Required |
|---|---|---|---|
| `DATABASE_URL` | api, agent-worker | PostgreSQL connection string | Yes |
| `TEMPORAL_HOST` | api, agent-worker | Temporal Frontend address | Yes |
| `JWT_SECRET` | api | 256-bit secret for JWT signing | Yes |
| `DOCKER_SOCKET` | api | Docker socket path | Yes |
| `OLLAMA_HOST` | agent-worker | Ollama server base URL | Yes |
| `SPECTER_LLM_MODEL` | agent-worker | LLM model name | Yes |
| `SPECTER_EMBED_MODEL` | agent-worker | Embedding model name | Yes |
| `WORKSPACE_ROOT` | agent-worker | Host path for repo workspaces | Yes |
| `SPECTER_MAX_REPO_SIZE_MB` | agent-worker | Maximum cloneable repo size | No (default: 500) |
| `SPECTER_CONTAINER_CPU` | api | CPU limit for test containers | No (default: 2) |
| `SPECTER_CONTAINER_MEMORY` | api | Memory limit for test containers | No (default: 2g) |
| `SPECTER_CONTAINER_TIMEOUT` | api | Timeout for test containers (seconds) | No (default: 600) |
| `RUST_LOG` | api | Rust log level | No (default: info) |
| `LOG_LEVEL` | agent-worker | Python log level | No (default: INFO) |

### 6.3 Volume Mounts Summary

| Volume | Mount Point | Purpose |
|---|---|---|
| `specter_workspaces` | `/workspaces` | Cloned repository workspaces |
| `postgres_data` | `/var/lib/postgresql/data` | PostgreSQL data |
| `ollama_models` | `/root/.ollama` | Downloaded Ollama model weights |
| `/var/run/docker.sock` | `/var/run/docker.sock:ro` | Docker socket for container management |

### 6.4 Port Mappings

| Port | Service | Description |
|---|---|---|
| 3000 | frontend | Next.js dev server |
| 8080 | api | Rust/Axum REST + WebSocket |
| 5432 | postgres | PostgreSQL |
| 7233 | temporal | Temporal gRPC Frontend |
| 8233 | temporal | Temporal Web UI |
| 11434 | ollama | Ollama inference API |
| 16686 | jaeger | Jaeger trace UI |
| 9090 | prometheus | Prometheus metrics UI |
| 4317 | otel-collector | OTLP gRPC receiver |
