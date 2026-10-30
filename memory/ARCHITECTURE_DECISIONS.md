# SPECTER — Architecture Decision Records (ADRs)

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
