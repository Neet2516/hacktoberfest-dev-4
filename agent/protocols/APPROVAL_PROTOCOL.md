# SPECTER Human Approval Protocol

## 1. Principle of Human-in-the-Loop Sovereignty
As mandated by **PRD Section 11 & FR-13**:
- SPECTER agents have **NO authority** to push branches to upstream repositories, merge code, or publish public pull requests autonomously.
- Remote mutation of external GitHub repositories strictly requires explicit, authenticated human approval.

---

## 2. Approval Gate Trigger

The Human Approval Gate is triggered **only** after all preceding automated quality gates have passed:
1. `Repository Archaeologist`: Context analyzed and recorded in Ghost Memory.
2. `Issue Investigator`: Issue reproduced and repair specification validated.
3. `Ghost Repairer`: Minimal patch generated.
4. `Adversarial Reviewer`: Patch independently audited and marked `APPROVED`.
5. `Test Engineer`: Clean test execution inside isolated Docker container with zero regressions.

---

## 3. Approval Request Package

When the gate is reached, the Resurrection Coordinator compiles and freezes the complete maintenance package:

```json
{
  "approval_request_id": "appr_9981273",
  "task_id": "SPECTER-094",
  "repository": "octocat/hello-world",
  "target_branch": "fix/specter-issue-42",
  "summary": "Fix null dereference in parser when processing empty documents",
  "artifacts": {
    "patch_diff_url": "/api/v1/tasks/SPECTER-094/patch",
    "review_report_url": "/api/v1/tasks/SPECTER-094/review",
    "test_verification_url": "/api/v1/tasks/SPECTER-094/tests",
    "investigation_report_url": "/api/v1/tasks/SPECTER-094/investigation"
  },
  "metrics": {
    "lines_added": 4,
    "lines_removed": 1,
    "files_changed": 1,
    "test_duration_seconds": 12.4,
    "total_agent_cycles": 1
  },
  "expires_at": "2026-11-07T00:00:00Z"
}
```

---

## 4. Human Decision Outcomes

The human supervisor may take one of three actions via the SPECTER UI or authenticated API:

### Action A: APPROVE
- Human clicks "Approve and Submit PR".
- Coordinator unseals the write-scoped GitHub credentials from the secure vault (never exposed to LLMs).
- Coordinator creates branch `specter/issue-<id>-fix`.
- Coordinator pushes minimal patch commit and opens Pull Request with formatted maintenance report.
- Task status transitions to `COMPLETED`.

### Action B: REQUEST REVISION
- Human provides explicit feedback notes.
- Coordinator injects human feedback into task context.
- Task transitions back to `IN-PROGRESS` assigned to Ghost Repairer or Issue Investigator.
- Retry counter is reset to 1 for human-guided iteration.

### Action C: REJECT / ABORT
- Human rejects proposal entirely.
- Coordinator destroys temporary workspace and cleans up test containers.
- Rejection rationale is recorded in Ghost Memory (`memory/ARCHITECTURE_DECISIONS.md` and repository memory store) to prevent identical unsuccessful attempts in the future.
- Task status transitions to `BLOCKED` or `ABORTED`.
