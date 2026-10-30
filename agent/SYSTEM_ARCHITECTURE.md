# SPECTER System Architecture (Agent-Centric View)

**Version:** 1.0.0
**Audience:** Agent developers, system operators, security reviewers

---

## 1. System Overview

SPECTER is a multi-agent AI system for autonomous repository maintenance. The architecture centers on six specialized agents coordinated by a Temporal workflow engine, backed by a Next.js frontend, a Rust/Axum API layer, and a Python agent orchestration runtime.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SPECTER SYSTEM BOUNDARY                           │
│                                                                           │
│  ┌─────────────────┐     ┌──────────────────────────────────────────┐   │
│  │   Next.js UI    │────▶│           Rust / Axum API                │   │
│  │  (Port 3000)    │◀────│           (Port 8080)                    │   │
│  └─────────────────┘     └──────────────┬───────────────────────────┘   │
│                                          │                               │
│                           ┌──────────────▼───────────────────────────┐  │
│                           │        Temporal Workflow Engine           │  │
│                           │   (Task State Machine + Orchestration)   │  │
│                           └──────────┬────────────────────┬──────────┘  │
│                                      │                    │              │
│                     ┌────────────────▼──┐          ┌──────▼───────────┐ │
│                     │   Python Agent    │          │   PostgreSQL     │ │
│                     │   Orchestration   │◀────────▶│   + pgvector     │ │
│                     │   Runtime         │          │   (Port 5432)    │ │
│                     └──────────┬────────┘          └──────────────────┘ │
│                                │                                         │
│              ┌─────────────────┼─────────────────────────┐              │
│              │                 │                           │              │
│  ┌───────────▼──┐  ┌──────────▼───────┐  ┌──────────────▼──────────┐   │
│  │ Resurrection │  │   Archaeologist  │  │   Issue Investigator    │   │
│  │ Coordinator  │  │   Agent          │  │   Agent                 │   │
│  └───────────┬──┘  └──────────────────┘  └─────────────────────────┘   │
│              │                                                            │
│  ┌───────────▼──┐  ┌──────────────────┐  ┌─────────────────────────┐   │
│  │    Ghost     │  │   Adversarial    │  │   Test Engineer         │   │
│  │   Repairer   │  │   Reviewer       │  │   Agent                 │   │
│  └──────────────┘  └──────────────────┘  └─────────────────────────┘   │
│                                                                           │
│  ┌──────────────────────────┐    ┌────────────────────────────────────┐  │
│  │  Ollama / Gemma LLM      │    │  Docker Isolation Layer            │  │
│  │  (Port 11434)            │    │  (Test Sandbox Containers)         │  │
│  └──────────────────────────┘    └────────────────────────────────────┘  │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
           │                                          │
           ▼                                          ▼
  ┌─────────────────┐                    ┌─────────────────────────┐
  │   GitHub API    │                    │  Cloned Repository       │
  │   (External)    │                    │  Workspace (Isolated FS) │
  └─────────────────┘                    └─────────────────────────┘
```

---

## 2. Agent Communication Topology

Agents communicate exclusively through structured messages stored in PostgreSQL and orchestrated by Temporal. **Agents do not communicate peer-to-peer** — all inter-agent communication flows through the Coordinator.

```
                    ┌──────────────────────┐
                    │  Resurrection        │
                    │  Coordinator         │
                    │  (Hub)               │
                    └──┬──┬──┬──┬──┬──────┘
                       │  │  │  │  │
          ┌────────────┘  │  │  │  └────────────────┐
          │               │  │  │                    │
          ▼               │  │  ▼                    ▼
  ┌───────────────┐       │  │  ┌───────────────┐   ┌───────────────┐
  │ Repository    │       │  │  │ Ghost         │   │ Test          │
  │ Archaeologist │       │  │  │ Repairer      │   │ Engineer      │
  └───────────────┘       │  │  └───────────────┘   └───────────────┘
                          │  │
          ┌───────────────┘  └────────────────────┐
          ▼                                        ▼
  ┌───────────────┐                       ┌───────────────┐
  │ Issue         │                       │ Adversarial   │
  │ Investigator  │                       │ Reviewer      │
  └───────────────┘                       └───────────────┘
```

**Message flow rules:**
- All messages use the `agent-message` JSON schema (see `schemas/agent-message.schema.json`)
- Coordinator is the only agent that can address messages to multiple other agents
- Specialist agents address replies only to the Coordinator
- Messages are persisted to PostgreSQL before delivery; no in-memory-only messaging

---

## 3. Data Flow Between Agents

```
Step 1: INTAKE
  GitHub API ──► Coordinator
  [Fetches: issue metadata, repo URL, labels, existing PRs]

Step 2: REPOSITORY ANALYSIS
  Coordinator ──► Archaeologist
  Archaeologist ──[reads]──► Git Clone (isolated workspace)
  Archaeologist ──[parses]──► Tree-sitter
  Archaeologist ──[stores]──► PostgreSQL (repo map, embeddings via pgvector)
  Archaeologist ──► Coordinator (repo_analysis output)

Step 3: ISSUE INVESTIGATION
  Coordinator ──► Investigator
  Investigator ──[reads]──► PostgreSQL (repo map + embeddings)
  Investigator ──[queries]──► Ollama/Gemma (semantic search, root cause)
  Investigator ──[reads]──► GitHub API (issue thread, linked PRs)
  Investigator ──► Coordinator (investigation_report output)

Step 4: REPAIR
  Coordinator ──► Ghost Repairer
  Ghost Repairer ──[reads]──► PostgreSQL (repo map + investigation report)
  Ghost Repairer ──[queries]──► Ollama/Gemma (patch generation)
  Ghost Repairer ──[writes]──► Isolated Git workspace (patch files)
  Ghost Repairer ──► Coordinator (patch_proposal output)

Step 5: REVIEW
  Coordinator ──► Adversarial Reviewer
  Adversarial Reviewer ──[reads]──► Patch files (isolated workspace)
  Adversarial Reviewer ──[reads]──► PostgreSQL (repo map, test history)
  Adversarial Reviewer ──[queries]──► Ollama/Gemma (review analysis)
  Adversarial Reviewer ──► Coordinator (review_report output)

Step 6: TESTING  [Human approval gate AG-01 before this step]
  Coordinator ──► Test Engineer
  Test Engineer ──[runs]──► Docker sandbox (isolated container)
  Test Engineer ──[reads]──► Container output (test results)
  Test Engineer ──► Coordinator (test_results output)

Step 7: PR CREATION  [Human approval gate AG-02]
  Coordinator ──► GitHub API (create PR)
  Coordinator ──► PostgreSQL (task status: COMPLETED)
```

---

## 4. External Service Dependencies Per Agent

| Agent | GitHub API | Git CLI | Docker | Ollama/Gemma | PostgreSQL | Temporal | Tree-sitter |
|-------|-----------|---------|--------|-------------|-----------|---------|------------|
| Coordinator | R: issues, repo; W: PR creation | — | — | Optional | RW: task state | RW: workflow state | — |
| Archaeologist | R: repo metadata | R: clone, log, diff | — | R: embeddings | W: repo map, embeddings | R: task state | R: parse source |
| Investigator | R: issue thread, comments | R: diff, blame | — | R: inference | R: repo map; W: investigation | R: task state | — |
| Ghost Repairer | — | R+W: branch, patch apply | — | R: patch generation | R: repo map, investigation; W: patch record | R: task state | R: validate patch AST |
| Adversarial Reviewer | R: PR history, similar issues | R: diff of patch | — | R: review analysis | R: everything; W: review report | R: task state | R: parse patched code |
| Test Engineer | — | — | RW: run containers | — | R: test specs; W: test results | R: task state | — |

**Access Mode Key:** R = Read only, W = Write, RW = Read + Write, — = No access

---

## 5. Isolation Boundaries

### 5.1 Repository Code Isolation
```
┌─────────────────────────────────────────────────┐
│  Docker Container (per test run)                │
│  ┌─────────────────────────────────────────┐    │
│  │  /repo  (read-only bind mount)          │    │
│  │  /tmp   (ephemeral write)               │    │
│  │  No network (default)                   │    │
│  │  CPU: 2 cores max                       │    │
│  │  Memory: 2GB max                        │    │
│  │  Timeout: 10 minutes max                │    │
│  └─────────────────────────────────────────┘    │
│  Container destroyed after run                  │
└─────────────────────────────────────────────────┘
         ▲
         │ (read-only mount)
┌────────┴────────────────────────────────────────┐
│  Isolated Workspace (per task)                  │
│  /workspaces/<task-id>/                         │
│  Destroyed on task completion or failure        │
└─────────────────────────────────────────────────┘
```

### 5.2 LLM Isolation
- Ollama/Gemma runs on the host but is accessed via HTTP API only
- Agents send prompts; they receive completions — no credential data ever in prompts
- LLM has no access to databases, filesystems, or external APIs

### 5.3 Credential Isolation
```
┌──────────────────────────────────────┐
│  Environment Variables (host only)   │
│  GITHUB_TOKEN, DATABASE_URL, etc.    │
└────────────────┬─────────────────────┘
                 │ Injected by orchestration runtime
                 ▼
┌──────────────────────────────────────┐
│  Temporal Worker Process             │
│  (has credentials, manages calls)    │
│                                      │
│  Agent LLM Prompts ────────────────► │ (credentials NEVER included)
└──────────────────────────────────────┘
```

---

## 6. State Management Responsibilities

| State Type | Owner | Storage | Access |
|-----------|-------|---------|--------|
| Task lifecycle state | Coordinator | Temporal + PostgreSQL tasks table | Coordinator writes; agents read own task |
| Workflow execution state | Temporal | Temporal event history | Coordinator writes; Temporal manages |
| Repository map & AST data | Archaeologist produces; PostgreSQL stores | PostgreSQL repo_analysis table | All agents read; only Archaeologist writes |
| Embeddings (semantic vectors) | Archaeologist produces; pgvector stores | PostgreSQL (pgvector extension) | Investigator + Repairer read |
| Investigation reports | Investigator produces | PostgreSQL investigation_reports table | Repairer + Reviewer read |
| Patch artifacts | Ghost Repairer produces | Isolated workspace + PostgreSQL patches table | Reviewer + Test Engineer read |
| Review reports | Adversarial Reviewer produces | PostgreSQL review_reports table | Coordinator + human read |
| Test results | Test Engineer produces | PostgreSQL test_results table | Coordinator + human read |
| Audit log | All agents write | PostgreSQL audit_log table (append-only) | Human reads; no agent deletes |
| Human approvals | Human | PostgreSQL approvals table | Coordinator reads to unblock gates |

---

*Last updated: See git history. Do not modify this document without updating the version.*
