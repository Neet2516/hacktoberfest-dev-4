# SPECTER Failure Recovery Procedures

**Version:** 1.0.0
**Applies To:** All SPECTER tasks and agents

---

## 1. Agent Failure Detection

### 1.1 Failure Signals

The Coordinator detects agent failure through the following signals:

| Signal | Detection Method | Severity |
|--------|-----------------|----------|
| **Timeout** | Temporal workflow timer exceeds phase timeout | HIGH |
| **Schema validation failure** | Output fails JSON Schema validation | MEDIUM–HIGH |
| **Confidence below floor** | Output confidence < configured minimum | MEDIUM |
| **Security violation** | Forbidden content (credentials, self-modification attempt) detected | CRITICAL |
| **Fabrication detected** | Evidence reference resolves to non-existent artifact | CRITICAL |
| **Ollama unreachable** | HTTP health check to port 11434 fails | HIGH |
| **Docker daemon failure** | Docker API returns error or times out | HIGH |
| **PostgreSQL connection lost** | DB connection pool exhausted or refused | CRITICAL |
| **GitHub API rate-limited** | HTTP 429 response | LOW (retryable) |
| **Agent process crash** | Temporal activity heartbeat missed | HIGH |
| **Scope violation** | Agent accesses files/APIs outside contract | CRITICAL |

### 1.2 Heartbeat Monitoring
Every agent activity sends a Temporal heartbeat every 60 seconds. A missed heartbeat triggers the Coordinator's failure handler for that activity. Activities are configured with `heartbeat_timeout = 90s`.

### 1.3 Health Check Schedule
The Coordinator runs periodic health checks at task start and between phases:

```
┌─── Phase boundary health check ───┐
│  1. Temporal worker alive?         │
│  2. PostgreSQL reachable?          │
│  3. Ollama reachable? (if needed)  │
│  4. Docker daemon alive? (if needed) │
│  5. GitHub API accessible?         │
└────────────────────────────────────┘
```

---

## 2. Task State Preservation on Failure

### 2.1 State Snapshot Policy
Before each phase begins, the Coordinator writes a checkpoint to PostgreSQL:

```sql
INSERT INTO task_checkpoints (
  task_id, phase, checkpoint_at, 
  completed_phases, 
  artifact_refs,       -- JSON array of all produced artifacts so far
  last_successful_phase
) VALUES (...);
```

This ensures that on failure, the system knows exactly which phases completed successfully and what artifacts were produced.

### 2.2 Preserved Artifacts
The following are NEVER deleted on agent failure:

| Artifact | Storage Location | Preserved On |
|---------|-----------------|--------------|
| Repository clone | `/workspaces/<taskId>/repo` | Preserved until task COMPLETED or operator cleanup |
| Repo analysis | PostgreSQL `repo_analysis` table | Always preserved |
| Investigation report | PostgreSQL `investigation_reports` table | Always preserved |
| Patch proposal (last) | PostgreSQL `patches` table | Always preserved |
| Review reports | PostgreSQL `review_reports` table | Always preserved |
| Test results | PostgreSQL `test_results` table | Always preserved |
| Audit log entries | PostgreSQL `audit_log` table (append-only) | **Never deleted** |
| Docker container logs | PostgreSQL `container_logs` table | Always preserved |
| Agent outputs (all attempts) | PostgreSQL `agent_outputs` table | All attempts preserved |

### 2.3 Failed Outputs
Failed or invalid outputs are **not discarded** — they are stored with a `status = FAILED` and `failure_reason` field. This allows post-hoc analysis of what went wrong.

---

## 3. Retry Strategies Per Agent Type

### 3.1 Repository Archaeologist Recovery

```
Failure Type          → Recovery Action
─────────────────────────────────────────────────────────────────
Timeout               → Kill activity, re-clone if workspace corrupted,
                        restart analysis from scratch
Tree-sitter crash     → Skip AST for failing file, log warning, continue
                        (partial repo map is acceptable)
Embedding failure     → Retry embedding only; continue without if 3 failures
                        (Investigator will fall back to keyword search)
Low confidence        → Widen analysis scope, re-run once;
                        if still low → human escalation
Disk full             → BLOCKED immediately; alert operator
```

### 3.2 Issue Investigator Recovery

```
Failure Type          → Recovery Action
─────────────────────────────────────────────────────────────────
Timeout               → Kill activity, retry with reduced context window
                        (fewer issue comments, fewer similar issues)
LLM inference error   → Retry up to 3 times; if all fail → BLOCKED
Confidence < 0.60     → Escalate to human with partial findings;
                        do NOT fabricate a root cause
No relevant files     → Report "unable to localize" to Coordinator;
                        Coordinator escalates to human
pgvector query fail   → Fall back to keyword search in repo map;
                        note degraded mode in output
```

### 3.3 Ghost Repairer Recovery

```
Failure Type          → Recovery Action
─────────────────────────────────────────────────────────────────
Patch AST invalid     → Discard patch, retry with different strategy;
                        after 3 attempts → BLOCKED
Patch too large       → Request narrower scope from Coordinator;
                        split if Coordinator approves
LLM inference error   → Retry with fallback prompt (see REPAIR_PROMPTS.md)
Patch apply failure   → Reset workspace clone, retry; after 2: BLOCKED
Scope violation       → Reject patch, log violation, retry with
                        explicit scope constraint in prompt
```

### 3.4 Adversarial Reviewer Recovery

```
Failure Type          → Recovery Action
─────────────────────────────────────────────────────────────────
Timeout               → Kill activity, retry with reduced analysis depth
LLM inference error   → Retry up to 2 times; if fail → partial review
                        with explicit "review incomplete" flag
Cannot access patch   → BLOCKED (artifact store failure)
Security finding HIGH → Do NOT retry; escalate to human immediately
```

### 3.5 Test Engineer Recovery

```
Failure Type          → Recovery Action
─────────────────────────────────────────────────────────────────
Docker start failure  → Retry 3 times (10s, 30s, 60s backoff);
                        check Docker daemon health; after 3: BLOCKED
Container timeout     → Kill container, record timeout as TEST_TIMEOUT;
                        report to Coordinator as ERROR verdict
Test framework error  → Log error, report as INFRASTRUCTURE_ERROR;
                        Coordinator decides retry vs. BLOCKED
Container escape attempt → CRITICAL: halt immediately, alert, BLOCKED
OOM killed            → Retry with lower memory; if OOM again: BLOCKED
All tests fail        → Not an infrastructure error; report ALL_FAIL verdict
                        to Coordinator; Coordinator routes back to Repairer
```

---

## 4. Escalation Path to Human

```
[AGENT FAILURE DETECTED]
          │
          ▼
[Retryable?]
  YES → Retry (up to max attempts per policy)
          │
          ▼ (max retries exhausted or non-retryable)
[COORDINATOR ASSESSMENT]
  Can task continue with partial output?
    YES → Continue with degraded mode, flag in task record
    NO  → Task → BLOCKED
          │
          ▼
[HUMAN ESCALATION TRIGGERED]
  Coordinator records in task:
    - escalation_reason
    - failing_phase
    - attempts_made
    - partial_artifacts_available
    - recommended_action (retry / manual_fix / abandon)
  
  Notification sent via:
    1. Next.js UI alert (task appears in BLOCKED queue)
    2. Configured webhook (if operator set up)
  
  Human options:
    ┌─ RETRY: Reset retry counter, restart failed phase
    ├─ SKIP: Mark phase as manually-reviewed, continue
    ├─ REASSIGN: Human provides manual input for that phase
    └─ ABANDON: Task → ABANDONED (preserved in DB, workspace cleaned)
```

### 4.1 Escalation SLAs
- **CRITICAL failures** (security violation, fabrication, container escape): Immediate notification
- **HIGH failures** (agent crash, DB connection loss): Within 5 minutes
- **MEDIUM failures** (low confidence, partial output): Within 30 minutes
- **LOW failures** (rate limit, transient API error): Resolved automatically; notify only if escalated to human

---

## 5. Unrecoverable Failure Conditions

The following constitute **unrecoverable failures** — the task is halted immediately with no automatic retry:

| Condition | Reason |
|-----------|--------|
| Security violation (credential in prompt/output) | Cannot proceed; integrity compromised |
| Fabricated evidence reference detected | Trust in agent output destroyed |
| Agent self-modification attempt | Agent operating outside charter |
| Docker container escape | Sandbox breached; security incident |
| Agent accessing tool outside its contract | Authorization violation |
| Conflicting task for same issue is active | Concurrency conflict |
| Repository deleted or made private mid-task | Source unavailable |
| PostgreSQL audit log write failure | Cannot maintain audit trail |

**On unrecoverable failure:**
1. Task status → `BLOCKED` (with `unrecoverable: true` flag)
2. All active agent activities halted via Temporal cancellation signal
3. Security violations → additional `security_incident` record created
4. Human notified immediately
5. Workspace preserved for forensic analysis (not auto-cleaned)

---

## 6. Restoring from BLOCKED State

### 6.1 What BLOCKED Means
A BLOCKED task is one where:
- Automatic retry has been exhausted, OR
- An unrecoverable condition was detected, OR
- Human intervention is required

The task record contains `blocked_reason`, `blocked_at`, `blocked_phase`, and `recommended_action`.

### 6.2 Restoration Procedure

**Step 1: Human Assessment**
Review in the Next.js UI:
- Which phase failed and why
- What partial artifacts exist
- Retry count and failure messages
- Whether the failure is in SPECTER or in the target repository

**Step 2: Choose Resolution Path**

| Scenario | Action |
|---------|--------|
| Transient infrastructure failure (DB, Docker, API) | Fix infrastructure → operator clicks "Resume from checkpoint" |
| LLM quality issue (bad patch, low confidence) | Provide human guidance in task notes → "Retry with guidance" |
| Fundamental issue (bug in agent logic) | File SPECTER bug → "Abandon task" → fix SPECTER → create new task |
| Repository issue (test suite broken independently) | Document in task notes → "Manual resolution" |

**Step 3: Resume**
- "Resume from checkpoint" restores the task to the last successful phase boundary
- Retry counters are reset for the resuming phase
- Resumption is recorded in audit log with human actor ID

**Step 4: Post-Mortem**
For any task that reaches BLOCKED status:
- An automatic post-mortem entry is created in `task_postmortems` table
- Contains: failure timeline, retry history, resolution action, time-to-resolution
- Used for SPECTER system improvement

---

*Failure recovery procedures are tested in the SPECTER integration test suite. See `/tests/integration/failure-recovery/` for test scenarios.*
