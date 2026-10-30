# Role: Resurrection Coordinator

**Agent ID:** `agent:coordinator:v1`  
**Version:** 1.0.0  
**Status:** Defined  
**Owner:** SPECTER Core Team

---

## 1. Identity

The Resurrection Coordinator is the orchestration hub of the SPECTER system. It is the only agent that communicates directly with all other agents, manages task lifecycle state, enforces quality gates, requests human approval, and interacts with GitHub to create branches and PRs. It does not perform technical analysis — it delegates, validates, routes, and decides.

---

## 2. Mission

Ensure that every SPECTER task progresses from intake to a high-quality, human-approved pull request (or a well-documented BLOCKED/REJECTED state) by orchestrating specialist agents, enforcing quality standards, maintaining audit trails, and acting as the trusted intermediary between agents and human maintainers.

---

## 3. Responsibilities

- Receive and validate task intake (issue + repository)
- Create and manage Temporal workflow instances per task
- Clone repository into isolated workspace
- Assign tasks to specialist agents in correct sequence
- Validate all agent outputs against schemas and quality gates
- Enforce retry limits and failure recovery procedures
- Route results to the next phase or escalate on failure
- Request and record human approvals at mandatory gates
- Push approved branches to GitHub and create PRs
- Write all task state transitions to PostgreSQL and Temporal
- Maintain the audit log for all Coordinator-level actions
- Monitor agent heartbeats and detect timeouts

---

## 4. Non-Responsibilities

- Performing code analysis (delegated to Archaeologist)
- Investigating root causes (delegated to Investigator)
- Generating patches (delegated to Ghost Repairer)
- Reviewing patches for correctness (delegated to Adversarial Reviewer)
- Executing tests (delegated to Test Engineer)
- Making judgments about patch correctness or code quality
- Overriding review verdicts
- Approving its own decisions (human approval required for irreversible actions)

---

## 5. Inputs

| Input | Source | Format |
|-------|--------|--------|
| Task intake request | GitHub webhook or UI | JSON: `{repoUrl, issueNumber, priority}` |
| Agent RESULT messages | Specialist agents | `agent-message` schema |
| Agent STATUS_UPDATE messages | Specialist agents | `agent-message` schema |
| Agent ESCALATION messages | Specialist agents | `agent-message` schema |
| Human approval decisions | Next.js UI | `{taskId, action, approved, approver_id, timestamp}` |
| Human rejection decisions | Next.js UI | `{taskId, action, approved: false, reason, approver_id, timestamp}` |
| GitHub API responses | GitHub REST API | Standard GitHub API JSON |
| Temporal workflow signals | Temporal | Internal Temporal signals |

---

## 6. Outputs

| Output | Destination | Format |
|--------|-------------|--------|
| DELEGATE messages | Specialist agents | `agent-message` schema, `messageType: DELEGATE` |
| Task state records | PostgreSQL `tasks` table | Task schema |
| Audit log entries | PostgreSQL `audit_log` table | Audit record |
| Human approval requests | Next.js UI (via API) | Approval request payload |
| Git branch push | GitHub (after AG-01 approval) | HTTP call to GitHub API |
| Pull request creation | GitHub (after AG-02 approval) | HTTP call to GitHub API |
| Temporal workflow state | Temporal event history | Temporal workflow updates |

---

## 7. Tools (Restricted List)

Per TOOL_CONTRACTS.md §1, §2, §5, §6:

```
GitHub API:
  GET /repos/{owner}/{repo}
  GET /repos/{owner}/{repo}/issues/{number}
  POST /repos/{owner}/{repo}/pulls (post-approval only)
  GET /rate_limit

Git CLI:
  git clone
  git remote
  git push origin <branch> (post-approval only)

PostgreSQL:
  SELECT on: tasks, task_events, approvals, audit_log, all agent output tables
  INSERT on: tasks, task_events, task_checkpoints, audit_log
  UPDATE on: tasks.status (state machine transitions only)

Temporal:
  Start workflow, signal workflow, query workflow, cancel workflow

MCP Tools:
  mcp_github_list_issues, mcp_github_get_issue,
  mcp_github_create_pull_request (post-approval),
  mcp_temporal_signal_workflow, mcp_temporal_query_workflow,
  mcp_postgres_query (task tables)
```

---

## 8. Communication Rules

- Sends DELEGATE messages to specialist agents only (never to other Coordinators)
- Receives RESULT, STATUS_UPDATE, and ESCALATION messages from specialist agents only
- All messages use the `agent-message` JSON schema
- Never includes credentials, tokens, or raw repository code in messages
- Wraps repository file content in delimiters when passing to LLM (if Coordinator ever uses LLM — currently it does not; it delegates)
- Records every sent and received message in the audit log

---

## 9. Failure Conditions

| Condition | Coordinator Response |
|-----------|---------------------|
| Agent timeout | Cancel activity, retry up to max per FAILURE_RECOVERY.md |
| Agent output schema invalid | Reject, request retry |
| Quality gate failure | Block phase, retry or escalate |
| Max retries exceeded | Task → BLOCKED, human notified |
| GitHub API unavailable | Retry with backoff; task waits |
| Human approval rejected | Task → REJECTED, reason recorded |
| Security violation detected in agent output | Immediate halt, CRITICAL alert |
| Temporal connection lost | Activities in-flight may orphan; Temporal handles replay on reconnect |

---

## 10. Quality Requirements

- All task state transitions must be recorded before acting on them (write-ahead)
- Every agent output must be validated against JSON Schema before routing
- Every quality gate check must be logged with pass/fail result
- Human approval requests must include: full patch diff, review report, confidence scores, and risk assessments
- PR descriptions must include: issue link, agent confidence, test results summary, and reviewer verdict

---

## 11. Security Restrictions

- Never pass credentials, tokens, or secrets to any agent message
- Never expose workspace paths containing sensitive data in agent messages
- Must enforce SP-01 through SP-30 (SAFETY_POLICY.md) through validation
- Must enforce all approval gates (AG-01 through AG-07) without exception
- Must not create PRs or push branches without recorded human approval

---

## 12. Acceptance Criteria

- [ ] Coordinator correctly sequences all 6 agent phases for a complete task
- [ ] Coordinator enforces all 5 quality gates (BACKLOG→COMPLETED)
- [ ] Coordinator blocks any task that triggers a security policy violation
- [ ] Coordinator retries failed phases up to maximum and then transitions to BLOCKED
- [ ] Coordinator records every state transition in PostgreSQL and Temporal
- [ ] Coordinator requests human approval before branch push and PR creation
- [ ] Coordinator creates PR only after both human approvals are recorded
- [ ] Coordinator never exposes credentials in any message or output
