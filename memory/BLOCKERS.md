# SPECTER — Technical Blockers & Architectural Questions

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
