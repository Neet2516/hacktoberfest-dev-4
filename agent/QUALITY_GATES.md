# SPECTER Quality Gates

**Version:** 1.0.0
**Applies To:** All task state transitions

---

> Quality gates are non-negotiable checkpoints. No agent may bypass a gate. The Coordinator enforces all gates automatically; human review gates require explicit approval recorded in the `approvals` table.

---

## 1. Overview: Task State Machine

```
 BACKLOG ──► READY ──► IN-PROGRESS ──► REVIEW ──► AWAITING_APPROVAL ──► COMPLETED
                │            │             │                                   │
                │            │             │                                   │
              BLOCKED      BLOCKED      BLOCKED                            REJECTED
                                                        
         Gate 1         Gate 2        Gate 3        Gate 4 (human)      Gate 5 (human)
     (BACKLOG→READY) (READY→IN-PROG) (IN-PROG→REVIEW) (REVIEW→AWAIT)  (AWAIT→COMPLETE)
```

---

## 2. Gate 1: BACKLOG → READY

**Enforced by:** Coordinator (automated, at task intake)  
**Triggered when:** New task created in BACKLOG state

### Required Conditions

| Check | Validation | Failure Action |
|-------|-----------|----------------|
| **GQ1-01** Repository accessible | GitHub API returns 200 for repo metadata | Retry 3×; then BLOCKED |
| **GQ1-02** Issue exists and open | GitHub API confirms issue open state | Reject task (issue closed/not found) |
| **GQ1-03** No duplicate task | `tasks` table has no active task for `(repoUrl, issueNumber)` | Reject intake; return existing task ID |
| **GQ1-04** Workspace creatable | `/workspaces/<taskId>/` directory successfully created | BLOCKED (disk issue) |
| **GQ1-05** Temporal workflow startable | Temporal client creates workflow without error | Retry 3×; then BLOCKED |
| **GQ1-06** Task record persisted | PostgreSQL INSERT to `tasks` table succeeds | Retry 3×; then abort |
| **GQ1-07** Priority assigned | `priority` field is one of: P0, P1, P2, P3 | Default to P3 |
| **GQ1-08** Repository not on blocklist | `blocked_repositories` table check | Reject task |

**Gate 1 Failure Consequence:** Task remains in BACKLOG with `blocked_reason`. Operator is notified.

---

## 3. Gate 2: READY → IN-PROGRESS

**Enforced by:** Coordinator (automated, before delegating to Archaeologist)  
**Triggered when:** Coordinator begins Phase 0 (readiness check) + Phase 1 (cloning)

### Required Conditions

| Check | Validation | Failure Action |
|-------|-----------|----------------|
| **GQ2-01** Repository cloned | `/workspaces/<taskId>/repo/.git` exists | Retry 3×; then BLOCKED |
| **GQ2-02** Clone is not empty | At least 1 source file present | BLOCKED (empty repo) |
| **GQ2-03** Ollama health check | GET `http://localhost:11434/` returns 200 | Retry 3×; then BLOCKED |
| **GQ2-04** PostgreSQL available | Connection pool reports ≥ 1 available connection | Retry 3×; then BLOCKED |
| **GQ2-05** Archaeologist agent reachable | Temporal worker activity registered | Retry 3×; then BLOCKED |
| **GQ2-06** Task not superseded | Issue still open (re-verify) | Abandon task; notify |
| **GQ2-07** No concurrent task conflict | No other task entered IN-PROGRESS for same repo in last 5 min | Queue behind existing |

**Gate 2 Failure Consequence:** Task reverts to BLOCKED. Infrastructure issue logged. Human notified.

---

## 4. Gate 3: IN-PROGRESS → REVIEW

**Enforced by:** Coordinator (automated, after Ghost Repairer delivers patch)  
**Triggered when:** Ghost Repairer sends RESULT message with `outputType == "patch_proposal"`

### Sub-gates (all must pass):

#### GQ3-A: Archaeologist Output Validity
| Check | Validation | Failure Action |
|-------|-----------|----------------|
| **GQ3-A-01** Schema valid | Validates against `agent-output.schema.json` | Reject, re-run Archaeologist |
| **GQ3-A-02** Language detected | `languageStack` array non-empty | Continue with "unknown" + warning |
| **GQ3-A-03** File map non-empty | `fileMap` contains ≥ 1 entry | BLOCKED (empty repo analysis) |
| **GQ3-A-04** Evidence refs valid | All `evidenceRefs` resolve to stored artifacts | Reject, re-run Archaeologist |
| **GQ3-A-05** Confidence ≥ 0.50 | Archaeologist confidence ≥ 0.50 | BLOCKED (escalate) |

#### GQ3-B: Investigation Report Validity
| Check | Validation | Failure Action |
|-------|-----------|----------------|
| **GQ3-B-01** Schema valid | Validates against `agent-output.schema.json` | Reject, re-run Investigator |
| **GQ3-B-02** Root cause identified | `rootCause` field non-empty string | Escalate to human if 3 failures |
| **GQ3-B-03** Affected files listed | `affectedFiles` array non-empty | BLOCKED (cannot localize issue) |
| **GQ3-B-04** Confidence ≥ 0.60 | Investigator confidence ≥ 0.60 | Escalate to human |
| **GQ3-B-05** Evidence refs valid | All `evidenceRefs` resolve | Reject, re-run Investigator |

#### GQ3-C: Patch Proposal Validity
| Check | Validation | Failure Action |
|-------|-----------|----------------|
| **GQ3-C-01** Schema valid | Validates against `agent-output.schema.json` | Reject, re-run Repairer |
| **GQ3-C-02** Patch non-empty | `patchDiff` field contains valid unified diff | Reject, re-run Repairer |
| **GQ3-C-03** Lines changed ≤ 500 | Count of `+/-` lines in diff ≤ 500 | Reject; request minimal patch |
| **GQ3-C-04** Syntax valid | AST parse of patched files succeeds (Tree-sitter) | Reject, re-run Repairer |
| **GQ3-C-05** Scope respected | Modified files ⊆ (affectedFiles ∪ 2 adjacent) | Reject, scope violation logged |
| **GQ3-C-06** No forbidden patterns | Patch does not contain: API keys, passwords, shell injection, `rm -rf` | CRITICAL halt |
| **GQ3-C-07** Confidence ≥ 0.55 | Repairer confidence ≥ 0.55 | Escalate to human |
| **GQ3-C-08** No test file removal | Patch does not delete existing test files | Reject, re-run Repairer |

**Gate 3 Failure Consequence:** Task stays IN-PROGRESS. Failed phase re-runs (up to max retries). After max retries: BLOCKED.

---

## 5. Gate 4: REVIEW → COMPLETED (Pre-approval review gate)

**Enforced by:** Coordinator (automated on review report receipt) + Human (for approval)  
**Triggered when:** Adversarial Reviewer sends RESULT with `outputType == "review_report"`

### Required Conditions

| Check | Validation | Failure Action |
|-------|-----------|----------------|
| **GQ4-01** Schema valid | Validates against `review-report.schema.json` | Reject, re-run Reviewer |
| **GQ4-02** Verdict present | `verdict` ∈ {APPROVED, APPROVED_WITH_CHANGES, REJECTED, NEEDS_HUMAN_REVIEW} | Reject, re-run Reviewer |
| **GQ4-03** Findings non-empty | `findings` array has ≥ 1 entry | Reject (reviewer must always find something to comment) |
| **GQ4-04** Regression risk assessed | `regressionRisk` ∈ {LOW, MEDIUM, HIGH, CRITICAL} | Reject |
| **GQ4-05** Security risk assessed | `securityRisk` ∈ {NONE, LOW, MEDIUM, HIGH, CRITICAL} | Reject |
| **GQ4-06** No CRITICAL security | `securityRisk` ≠ CRITICAL without human approval | Auto-escalate to human |
| **GQ4-07** No CRITICAL regression | `regressionRisk` ≠ CRITICAL without human approval | Auto-escalate to human |
| **GQ4-08** Evidence refs valid | All `evidenceRefs` resolve | Reject |

**Verdict routing:**
- `APPROVED` → Proceed to branch push human approval gate (AG-01)
- `APPROVED_WITH_CHANGES` → Return to Ghost Repairer with reviewer corrections
- `REJECTED` → Coordinator evaluates root cause; may re-run Investigator → Repairer → Reviewer cycle
- `NEEDS_HUMAN_REVIEW` → Task status → AWAITING_APPROVAL; human assessment required before continuing

**Review cycle limit:** Maximum 3 Repairer → Reviewer cycles. After 3: task → BLOCKED.

---

## 6. Gate 5: AWAITING_APPROVAL → COMPLETED

**Enforced by:** Human (mandatory) + Coordinator (records outcome)  
**Triggered when:** Test Engineer reports ALL_PASS (or acceptable PARTIAL_PASS) and human is prompted for PR approval

### Required Conditions (all verified by Coordinator before presenting to human)

| Check | Validation | Failure Action |
|-------|-----------|----------------|
| **GQ5-01** Test results present | `test_results` record exists for task | Cannot present for approval |
| **GQ5-02** Test verdict acceptable | `verdict` ∈ {ALL_PASS, PARTIAL_PASS with documented pre-existing failures} | Return to Test Engineer / Repairer |
| **GQ5-03** Review approved | Latest `review_report.approved` == true | Cannot proceed to PR |
| **GQ5-04** Human approval for branch | `approvals` record with `action == "branch_push"` exists | Cannot proceed |
| **GQ5-05** Branch pushed | GitHub API confirms branch exists in remote | Cannot create PR |
| **GQ5-06** PR metadata complete | Title, body, labels, linked issue number ready | Coordinator fills defaults |
| **GQ5-07** Human PR approval | `approvals` record with `action == "pr_creation"` exists | Wait; no auto-proceed |
| **GQ5-08** PR created | GitHub API returns PR URL | Retry 3×; then BLOCKED |

**On human REJECT:** Task → REJECTED with rejection reason. All artifacts preserved. Task can be re-opened.

**Gate 5 Failure Consequence:** Task remains AWAITING_APPROVAL. Human must take action.

---

## 7. Gate Failure Consequences Summary

| Gate | Failure → | Max Retries | Human Alert |
|------|----------|-------------|-------------|
| Gate 1 | BACKLOG (remains) | 3 per check | If BLOCKED |
| Gate 2 | BLOCKED | 3 per check | Yes |
| Gate 3 | IN-PROGRESS (retry phase) | 3 per phase | If BLOCKED |
| Gate 4 | REVIEW cycle continues | 3 review cycles total | If BLOCKED or NEEDS_HUMAN |
| Gate 5 | AWAITING_APPROVAL (human decides) | N/A (human gate) | Yes (always) |

---

## 8. Gate Enforcement Responsibility

| Gate | Primary Enforcer | Secondary Enforcer | Logging |
|------|-----------------|-------------------|---------|
| Gate 1 | Coordinator (automated) | — | `task_events` table |
| Gate 2 | Coordinator (automated) | — | `task_events` table |
| Gate 3 | Coordinator (automated) | Adversarial Reviewer (catches missed issues) | `task_events` + `audit_log` |
| Gate 4 | Coordinator (automated) | Human reviewer (via UI) | `task_events` + `audit_log` |
| Gate 5 | Human (mandatory) | Coordinator (records decision) | `approvals` + `audit_log` |

---

*Quality gates cannot be disabled at runtime. Modifications to gate logic require a SPECTER system update with human operator approval.*
