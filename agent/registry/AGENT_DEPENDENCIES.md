# SPECTER Agent Dependencies

**Version:** 1.0.0

---

## 1. Service Dependencies Per Agent

### Dependency Severity Key
- **REQUIRED** — Agent cannot function without this service
- **DEGRADED** — Agent can function with reduced capability if unavailable
- **OPTIONAL** — Enhancement only; absence does not affect core function

| Service | Coordinator | Archaeologist | Investigator | Ghost Repairer | Adv. Reviewer | Test Engineer |
|---------|:-----------:|:-------------:|:------------:|:--------------:|:-------------:|:-------------:|
| **GitHub API** | REQUIRED | DEGRADED | REQUIRED | ❌ | DEGRADED | ❌ |
| **Git CLI** | REQUIRED (clone) | REQUIRED | REQUIRED | REQUIRED | REQUIRED | DEGRADED |
| **PostgreSQL** | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| **pgvector** | ❌ | REQUIRED | REQUIRED | DEGRADED | ❌ | ❌ |
| **Ollama/Gemma** | ❌ | REQUIRED | REQUIRED | REQUIRED | REQUIRED | ❌ |
| **Temporal** | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| **Tree-sitter** | ❌ | REQUIRED | ❌ | REQUIRED | DEGRADED | ❌ |
| **Docker** | ❌ | ❌ | ❌ | ❌ | ❌ | REQUIRED |
| **Workspace FS** | REQUIRED | REQUIRED | OPTIONAL | REQUIRED | REQUIRED | REQUIRED |

---

## 2. Inter-Agent Output Dependencies

### Dependency Flow

```
[GitHub / Operator]
        │
        ▼ (issue metadata, repo URL)
[Resurrection Coordinator]
        │
        ▼ (task delegation)
[Repository Archaeologist]
        │ produces: repo_analysis, file_map, embeddings
        ▼
[Issue Investigator] ─────────────── reads: repo_analysis, embeddings
        │ produces: investigation_report
        ▼
[Ghost Repairer] ─────────────────── reads: investigation_report, repo_analysis
        │ produces: patch_proposal (git diff + patched workspace)
        ▼
[Adversarial Reviewer] ─────────────reads: patch_proposal, investigation_report, repo_analysis
        │ produces: review_report (verdict + findings)
        ▼
[Human Approval Gate] ←───────────── Coordinator presents: patch + review + test plan
        │ (on approve)
        ▼
[Test Engineer] ──────────────────── reads: patch_proposal (applies in Docker)
        │ produces: test_results
        ▼
[Human Approval Gate (PR)] ←──────── Coordinator presents: full evidence package
        │ (on approve)
        ▼
[GitHub PR Created] ← Coordinator
```

### Dependency Table

| Agent | Depends On Output From | Specific Artifacts |
|-------|------------------------|-------------------|
| **Coordinator** | All agents | All agent outputs (for validation and routing) |
| **Archaeologist** | Coordinator | Task metadata (repoUrl, issueNumber, workspacePath) |
| **Investigator** | Archaeologist | `repo_analysis.id`, `file_map`, `embeddings` table rows for this task |
| **Ghost Repairer** | Investigator | `investigation_report.id`, `affectedFiles`, `rootCause`, `confidence` |
| **Ghost Repairer** | Archaeologist | `repo_analysis.id` (for style/architecture context) |
| **Adversarial Reviewer** | Ghost Repairer | `patch_proposal.id`, `patchDiff`, workspace patched files |
| **Adversarial Reviewer** | Investigator | `investigation_report.id` (to verify patch addresses root cause) |
| **Adversarial Reviewer** | Archaeologist | `repo_analysis.id` (for regression context) |
| **Test Engineer** | Ghost Repairer | `patch_proposal.id`, workspace with applied patch |
| **Test Engineer** | Coordinator | `testFramework`, `testCommand`, Docker image selection |

---

## 3. External Service Availability Requirements

### Startup Checks (performed by Coordinator before Phase 0)

```
Service              Health Check                         Required By
─────────────────────────────────────────────────────────────────────
GitHub API           GET /rate_limit → 200                Phase 1+
Ollama               GET http://localhost:11434/           Phase 3+
PostgreSQL           SELECT 1                             All phases
pgvector             SELECT * FROM pg_extension WHERE name='vector'  Phase 2+
Docker daemon        docker info                          Phase 7+
Temporal             Namespace describe                   All phases
Git                  git --version                        Phase 1+
Tree-sitter          python -c "import tree_sitter"       Phase 2+
```

If any REQUIRED service is unavailable at startup, the task waits up to 5 minutes for recovery before entering BLOCKED state.

---

## 4. Data Artifact Dependencies

### Artifact Lifecycle

| Artifact | Produced By | Consumed By | Storage | Retention |
|----------|-------------|-------------|---------|-----------|
| `repo_analysis` | Archaeologist | Investigator, Repairer, Reviewer | PostgreSQL + workspace | Task lifetime + 30 days |
| `file_map` | Archaeologist | Investigator, Repairer | PostgreSQL | Task lifetime + 30 days |
| `embeddings` | Archaeologist | Investigator, Repairer | pgvector | Task lifetime + 30 days |
| `investigation_report` | Investigator | Repairer, Reviewer, Coordinator | PostgreSQL | Task lifetime + 30 days |
| `patch_proposal` | Ghost Repairer | Reviewer, Test Engineer, Coordinator, Human | PostgreSQL + workspace | Task lifetime + 30 days |
| `review_report` | Adversarial Reviewer | Coordinator, Human | PostgreSQL | Task lifetime + 30 days |
| `test_results` | Test Engineer | Coordinator, Human | PostgreSQL | Task lifetime + 30 days |
| `container_logs` | Test Engineer | Coordinator, Human, Audit | PostgreSQL | Task lifetime + 90 days |
| `audit_log` | All agents | Human, Operators | PostgreSQL (append-only) | Permanent |
| `approvals` | Human (via UI) | Coordinator | PostgreSQL | Permanent |

### Artifact Dependency Validation
The Coordinator validates artifact dependencies before delegating to each agent:
- All required upstream artifacts must exist in PostgreSQL with `status = COMPLETE`
- Artifact `task_id` must match the current task (cross-task access blocked)
- Artifacts must not be older than 24 hours without re-validation

---

## 5. Failure Cascade Analysis

| Failed Component | Affected Agents | Cascade Effect |
|-----------------|----------------|----------------|
| Ollama/Gemma | Investigator, Repairer, Reviewer | All three phases block; task → BLOCKED |
| PostgreSQL | All agents | Total system halt; all tasks → BLOCKED |
| GitHub API | Coordinator, Archaeologist, Investigator | Intake blocked; in-progress tasks can continue if clone succeeded |
| Docker daemon | Test Engineer | Test phase blocks; patch review can proceed; PR creation requires human decision |
| Tree-sitter | Archaeologist, Repairer | Partial repo map (text-based fallback); patch syntax validation degraded |
| Workspace FS | All agents | Task cannot proceed; task → BLOCKED |
| Temporal | All agents | Orchestration lost; activities may complete but state not recorded → BLOCKED |
| pgvector extension | Investigator | Falls back to keyword search; Repairer cannot do semantic search |

---

*This document should be updated whenever a new agent is added, a new service dependency is introduced, or an existing dependency changes.*
