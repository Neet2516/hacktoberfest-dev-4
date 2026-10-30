# SPECTER Execution Protocol

**Version:** 1.0.0
**Applies To:** All SPECTER tasks, all agent executions

---

## 1. Task Intake Procedure

### 1.1 Trigger Sources
Tasks enter SPECTER via one of:
1. **GitHub Webhook** — issue opened/labeled on a monitored repository
2. **Manual Entry** — operator submits task through Next.js UI
3. **Coordinator Discovery** — Coordinator identifies a related issue during investigation

### 1.2 Intake Steps

```
[TRIGGER RECEIVED]
       │
       ▼
[VALIDATE TRIGGER]
  ✓ Repository is public or operator has explicit access
  ✓ Issue exists and is open
  ✓ No duplicate task exists for same issue (check tasks table)
  ✓ Repository is not on blocklist
       │
       ▼
[CREATE TASK RECORD]
  - Generate taskId (UUID v4)
  - Set status: BACKLOG
  - Record: repoUrl, issueNumber, issueTitle, issuePriority
  - Timestamp: created_at (UTC)
       │
       ▼
[ENQUEUE IN TEMPORAL]
  - Create Temporal workflow instance: specter-task-<taskId>
  - Workflow receives: taskId, repoUrl, issueNumber
       │
       ▼
[STATUS: BACKLOG]
```

### 1.3 Intake Validation Rules
- Repository URL must match pattern: `https://github.com/<owner>/<repo>`
- Issue number must be a positive integer referencing an open issue
- Task deduplication key: `(repoUrl, issueNumber)` — reject if active task exists
- Priority assigned based on issue labels: `priority:critical` → P0, `bug` → P1, `enhancement` → P2, unlabeled → P3

---

## 2. Agent Assignment Rules

The Coordinator assigns agents based on the current workflow stage:

| Stage | Assigned Agent | Pre-condition |
|-------|---------------|---------------|
| Repository Analysis | Repository Archaeologist | Task in READY state; repo cloned successfully |
| Issue Investigation | Issue Investigator | Archaeologist output received and validated |
| Patch Generation | Ghost Repairer | Investigator output received; confidence ≥ 0.60 |
| Adversarial Review | Adversarial Reviewer | Repairer patch received and syntax-validated |
| Test Execution | Test Engineer | Reviewer verdict: APPROVED or APPROVED_WITH_CHANGES; human approval for branch push |
| PR Creation | Coordinator (directly) | Test Engineer: ALL_PASS; human approval for PR |

**Assignment is exclusive:** Only one agent is active per task at any time. The Coordinator waits for current agent completion before assigning the next.

---

## 3. Execution Sequence

### Phase 0: Readiness Check
```
Coordinator checks:
  □ Repository accessible (GitHub API health check)
  □ Ollama/Gemma reachable (health ping)
  □ PostgreSQL connected
  □ Docker daemon running (for later test phase)
  □ Workspace directory created for task
  
On any failure: task status → BLOCKED, reason logged
```

### Phase 1: Repository Cloning
```
Coordinator → [git clone <repoUrl> /workspaces/<taskId>/repo]
  ├─ Success: status remains READY, proceed
  └─ Failure: retry up to 3 times (5s, 15s, 30s backoff)
              After 3 failures: status → BLOCKED
```

### Phase 2: Repository Analysis (Archaeologist)
```
Coordinator sends: DELEGATE message to Archaeologist
  payload: { taskId, repoPath, issueNumber, issueTitle }

Archaeologist performs:
  1. Directory tree enumeration
  2. Language detection (file extensions, markers)
  3. Tree-sitter AST parsing of relevant files
  4. Dependency graph construction
  5. Semantic embedding generation (pgvector)
  6. Test infrastructure detection
  7. Contribution guidelines check (CONTRIBUTING.md, PR template)

Archaeologist sends: RESULT message to Coordinator
  payload: repo_analysis output (see agent-output.schema.json)

Coordinator validates:
  □ outputType == "repo_analysis"
  □ confidence ≥ 0.50
  □ evidenceRefs non-empty
  □ languageStack identified
  □ testFramework identified or "unknown"
  
Timeout: 10 minutes. On timeout → retry (see §5)
```

### Phase 3: Issue Investigation (Investigator)
```
Coordinator sends: DELEGATE message to Investigator
  payload: { taskId, issueNumber, repoAnalysisId, issueBody, issueComments }

Investigator performs:
  1. Issue body + comment semantic analysis
  2. Relevant file identification (pgvector similarity search)
  3. Code path tracing to issue manifestation point
  4. Root cause hypothesis generation (Ollama/Gemma)
  5. Confidence scoring
  6. Similar past issues search (pgvector)

Investigator sends: RESULT message to Coordinator
  payload: investigation_report output

Coordinator validates:
  □ outputType == "investigation_report"
  □ rootCause field non-empty
  □ confidence score present and in [0.0, 1.0]
  □ affectedFiles list non-empty
  □ If confidence < 0.60: status → NEEDS_HUMAN_REVIEW, escalate

Timeout: 15 minutes. On timeout → retry (see §5)
```

### Phase 4: Patch Generation (Ghost Repairer)
```
Coordinator sends: DELEGATE message to Ghost Repairer
  payload: { taskId, investigationReportId, affectedFiles, rootCause }

Ghost Repairer performs:
  1. Minimal change strategy selection
  2. Patch generation via Ollama/Gemma
  3. AST validation of generated patch (Tree-sitter)
  4. Patch application to workspace clone
  5. Diff generation and size check (max 500 lines changed)
  6. Architecture preservation check

Ghost Repairer sends: RESULT message to Coordinator
  payload: patch_proposal output (includes git diff)

Coordinator validates:
  □ outputType == "patch_proposal"
  □ patchDiff non-empty and valid unified diff format
  □ linesChanged ≤ 500
  □ No modification to files outside affectedFiles + 2 adjacent files max
  □ AST parse of patched files succeeds (no syntax errors)
  □ confidence ≥ 0.55

Timeout: 20 minutes. On timeout → retry (see §5)
```

### Phase 5: Adversarial Review (Adversarial Reviewer)
```
Coordinator sends: DELEGATE message to Adversarial Reviewer
  payload: { taskId, patchProposalId, repoAnalysisId, investigationReportId }

Adversarial Reviewer performs:
  1. Patch correctness challenge (does it actually fix the root cause?)
  2. Regression risk assessment (what could break?)
  3. Security surface analysis (does patch introduce vulnerabilities?)
  4. Scope check (does patch stay within boundaries?)
  5. Code quality assessment (style, naming, documentation)
  6. Alternative approach consideration

Adversarial Reviewer sends: RESULT message to Coordinator
  payload: review_report output
  verdict: one of: APPROVED | APPROVED_WITH_CHANGES | REJECTED | NEEDS_HUMAN_REVIEW

Coordinator validates:
  □ outputType == "review_report"
  □ verdict field present
  □ findings list non-empty (even for APPROVED)
  □ regressionRisk in [LOW, MEDIUM, HIGH, CRITICAL]
  □ securityRisk in [NONE, LOW, MEDIUM, HIGH, CRITICAL]
  □ If securityRisk in [HIGH, CRITICAL]: auto-escalate to human

Verdict routing:
  APPROVED → proceed to human approval gate AG-01
  APPROVED_WITH_CHANGES → return to Ghost Repairer for corrections
  REJECTED → Coordinator decides: retry Ghost Repairer or escalate
  NEEDS_HUMAN_REVIEW → escalate immediately

Max review cycles: 3 (Repairer → Reviewer). After 3: BLOCKED.

Timeout: 15 minutes. On timeout → retry (see §5)
```

### Phase 6: Human Approval Gate (AG-01 + Branch Push)
```
Coordinator notifies human via UI:
  - Summary of issue, patch, review report, test plan
  - Confidence scores and risk assessments
  - Diff viewer

Human actions:
  APPROVE → Coordinator pushes branch to GitHub (git push)
             Records approval in approvals table
  REJECT → Coordinator records rejection, task → REJECTED
           Human may provide rejection reason for retry

Timeout: No timeout (human decision). Task waits indefinitely in AWAITING_APPROVAL.
```

### Phase 7: Test Execution (Test Engineer)
```
Coordinator sends: DELEGATE message to Test Engineer
  payload: { taskId, patchProposalId, testFramework, repoPath }

Test Engineer performs:
  1. Docker container preparation (pre-built image selection)
  2. Repository mount (read-only) + patch application in container
  3. Test discovery (framework-appropriate)
  4. Test execution with timeout
  5. Result parsing and categorization
  6. Coverage delta computation (if coverage tooling present)

Test Engineer sends: RESULT message to Coordinator
  payload: test_results output
  verdict: ALL_PASS | PARTIAL_PASS | ALL_FAIL | ERROR

Coordinator validates:
  □ outputType == "test_results"
  □ verdict field present
  □ testCount ≥ 1
  □ containerExitCode matches reported verdict
  □ Docker container destroyed after run (verified by container list check)

Verdict routing:
  ALL_PASS → proceed to PR creation approval gate
  PARTIAL_PASS → Coordinator evaluates: if failing tests pre-existed, proceed; else → Repairer
  ALL_FAIL → return to Ghost Repairer (max 2 test-cycle retries)
  ERROR → retry (infrastructure error); after 3: BLOCKED

Timeout: 30 minutes (includes container startup + test run). 
On timeout → container killed, task → BLOCKED.
```

### Phase 8: PR Creation (Human Approval Gate AG-02)
```
Coordinator notifies human:
  - Final patch diff
  - Test results summary
  - Review report
  - PR draft (title, body, labels)

Human actions:
  APPROVE → Coordinator calls GitHub API to create PR
             Records approval in approvals table
             Task status → COMPLETED
  REJECT → Task status → REJECTED (with reason)
  REQUEST_CHANGES → Task may cycle back (human specifies which phase)
```

---

## 4. Output Validation at Each Step

Every agent output is validated by the Coordinator against:
1. **Schema validation** — JSON Schema `agent-output.schema.json`
2. **Semantic validation** — confidence score, non-empty required fields
3. **Security validation** — no credential patterns in output, no forbidden content
4. **Consistency validation** — evidenceRefs resolve to actual stored artifacts
5. **Scope validation** — output does not reference files/actions outside task scope

Validation failure codes:
- `SCHEMA_INVALID` → reject output, request retry
- `CONFIDENCE_TOO_LOW` → escalate to human
- `SECURITY_VIOLATION` → halt task immediately, alert
- `EVIDENCE_UNRESOLVABLE` → reject output, request retry with valid evidence
- `SCOPE_VIOLATION` → halt task, alert, escalate

---

## 5. Retry Logic

### Per-Agent Retry Policy

| Agent | Max Retries | Backoff | After Max Retries |
|-------|------------|---------|------------------|
| Archaeologist | 3 | 10s, 30s, 60s | BLOCKED |
| Investigator | 3 | 15s, 45s, 90s | BLOCKED or human escalation |
| Ghost Repairer | 3 | 20s, 60s, 120s | BLOCKED |
| Adversarial Reviewer | 2 | 15s, 45s | BLOCKED |
| Test Engineer | 3 | 30s, 60s, 120s | BLOCKED |
| PR Creation | 3 | 10s, 30s, 60s | BLOCKED (GitHub API issue) |

### Retry Conditions
- **Retryable:** Timeout, transient API error, LLM inference error, Docker startup failure
- **Not Retryable:** Schema validation failure (requires human fix), security violation, scope violation, fabrication detected

### State on Retry
Before retry, Coordinator:
1. Archives the failed output to the audit log (with failure reason)
2. Resets agent state for the retrying agent only
3. Preserves all prior successful phase outputs
4. Increments retry counter in task record

---

## 6. Timeout Policies

| Operation | Timeout | Action on Timeout |
|-----------|---------|------------------|
| GitHub API call | 30 seconds | Retry with exponential backoff |
| Git clone | 5 minutes | Retry; after 3: BLOCKED |
| Ollama/Gemma inference | 5 minutes | Retry; after 3: BLOCKED |
| Archaeologist phase | 10 minutes | Kill, retry phase |
| Investigator phase | 15 minutes | Kill, retry phase |
| Ghost Repairer phase | 20 minutes | Kill, retry phase |
| Adversarial Review phase | 15 minutes | Kill, retry phase |
| Docker container run | 10 minutes | Kill container, report ERROR |
| Test Engineer phase | 30 minutes | Kill, retry phase |
| Human approval wait | None (indefinite) | Task waits in AWAITING_APPROVAL |
| Total task lifetime | 24 hours | Coordinator escalates to human |

---

*All execution steps are recorded in the Temporal workflow history for replay and audit purposes.*
