# SPECTER Escalation Protocol

## 1. Purpose
The Escalation Protocol establishes formal mechanisms for handling runtime deadlocks, unresolvable agent disputes, repeated review/test failures, security tripwires, and ambiguous repository instructions.

---

## 2. Escalation Triggers

| Trigger Code | Severity | Trigger Description | Immediate System Action |
|---|---|---|---|
| `ESC-01` | CRITICAL | Security Policy Tripwire (e.g. prompt injection detected, credential access attempt, Docker breakout indicator) | Immediate process termination, workspace isolation, human security alert |
| `ESC-02` | HIGH | Review Rejection Budget Exhausted (> 3 consecutive rejections by Adversarial Reviewer) | Halt repair loop, mark task `BLOCKED`, notify supervisor with diff audit |
| `ESC-03` | HIGH | Test Suite Failure Loop (> 3 failed container test attempts on generated patches) | Preserve failed test container logs, transition task to `BLOCKED` |
| `ESC-04` | MEDIUM | Deadlock / Agent Timeout (agent unresponsive for > 2x timeout duration) | Force kill agent worker activity, retry once; escalate if persistent |
| `ESC-05` | MEDIUM | Ambiguous Issue Specification (Issue text contradictory or lacks reproduction info) | Escalate to human operator for issue clarification |
| `ESC-06` | LOW | Missing Test Infrastructure (Repository has no tests detected) | Prompt human whether to proceed without test verification or generate tests |

---

## 3. Escalation Chain

```
[Specialized Agent]
        │
        ▼ (Condition Triggered)
[Resurrection Coordinator]
        │
        ├── Can self-heal? (Retry <= 3, transient error) ──> Yes ──> Auto-Retry
        │
        └── No (Budget exhausted / Security tripwire)
                │
                ▼
      [Human Supervisor (UI/Alert)]
                │
        ┌───────┴───────┐
        ▼               ▼
   [Intervene]      [Abort Task]
```

---

## 4. Escalation Message Payload

```json
{
  "escalation_id": "esc_554412",
  "task_id": "SPECTER-068",
  "trigger_code": "ESC-02",
  "severity": "HIGH",
  "originating_agent": "adversarial_reviewer",
  "summary": "Ghost Repairer failed 3 consecutive review cycles due to persistent regression in public API contract.",
  "history": [
    {"attempt": 1, "verdict": "REQUEST_CHANGES", "reason": "Modified public function signature in src/lib.rs"},
    {"attempt": 2, "verdict": "REQUEST_CHANGES", "reason": "Removed deprecated method still used in tests"},
    {"attempt": 3, "verdict": "REQUEST_CHANGES", "reason": "Introduced unchecked unwrap() in error path"}
  ],
  "recommended_actions": [
    "Manually provide stricter repair constraints to Issue Investigator",
    "Allow minor public API modification via human override",
    "Mark issue as wont-fix / blocked"
  ],
  "timestamp": "2026-10-31T00:20:00Z"
}
```

---

## 5. Resolution Paths

1. **Human Override**: Human supervisor inspects findings in UI, optionally edits the repair specification or patch directly, and issues a resume command.
2. **Re-scoping**: Human narrows the issue scope or provides additional reproduction instructions.
3. **Graceful Abandonment**: If the repository is too degraded or the issue is invalid, the task is marked `BLOCKED`, Ghost Memory records the failure and rationale, and system resources are freed.
