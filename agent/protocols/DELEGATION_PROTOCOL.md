# SPECTER Task Delegation Protocol

## 1. Overview
The Delegation Protocol governs how the **Resurrection Coordinator** allocates tasks to specialized agents (Archaeologist, Investigator, Repairer, Reviewer, Test Engineer). It establishes criteria for task readiness, agent capability checks, assignment handshakes, concurrency boundaries, and timeout management.

---

## 2. Delegation Preconditions

Before the Coordinator may issue a `delegation` message for any task, the following quality gates must pass:
1. **Task State Verification**: The task must be in `READY` status in `tasks/ready/` or PostgreSQL state store.
2. **Dependency Resolution**: All prerequisite task IDs listed in `dependencies` must be in `COMPLETED` status with verified evidence.
3. **Agent Availability**: The target agent must not have exceeded its maximum concurrent task allocation (default: 1 active task per agent instance).
4. **Capability Match**: The assigned agent's registered capabilities in `agent/registry/AGENT_CAPABILITIES.md` must encompass all requirements of the task.

---

## 3. Delegation Workflow Sequence

```
Coordinator                       Specialized Agent                 Temporal Workflow
    │                                     │                                 │
    ├─── Check Task Ready & Deps ─────────┼────────────────────────────────>│
    ├─── Publish Delegation Message ─────>│                                 │
    │    (type: "delegation")             │                                 │
    │                                     ├─── Validate Payload & Context   │
    │<── Send Acknowledgment ─────────────┤                                 │
    │    (status: "in_progress")          │                                 │
    │                                     ├─── Record Task IN-PROGRESS ────>│
    │                                     │                                 │
    │                                     ├─── Execute Sub-Tasks            │
    │                                     │    (with Periodic Heartbeat)    │
    │                                     │                                 │
    │<── Deliver Agent Output ────────────┤                                 │
    │    (type: "output", status: "ready")│                                 │
```

---

## 4. Delegation Envelope

A delegation payload must contain:

```json
{
  "task_id": "SPECTER-068",
  "task_title": "Implement Ghost Repairer agent",
  "instructions": "Implement the core patch generation logic adhering to minimal diff principles.",
  "input_context": {
    "repository_url": "https://github.com/example/abandoned-project",
    "commit_sha": "9f83a21b",
    "workspace_path": "/var/specter/workspaces/ws_001",
    "investigation_report_ref": "out_inv_88291"
  },
  "constraints": {
    "timeout_seconds": 600,
    "max_retries": 3,
    "allowed_file_patterns": ["src/**/*.py", "tests/**/*.py"],
    "forbidden_file_patterns": [".github/**", "**/credentials*", "**/*.env"]
  }
}
```

---

## 5. Timeouts and Dead Agent Detection

- **Acknowledgment Timeout**: The assigned agent must respond with an `acknowledgment` message within **30 seconds** of delegation. If no ack is received, the Coordinator retries up to 2 times, after which the agent is flagged as `UNRESPONSIVE`.
- **Execution Heartbeat**: Long-running agents (> 60 seconds) must emit a `heartbeat` message every 30 seconds.
- **Hard Execution Timeout**: Each task defines a hard timeout (default: 600 seconds). If exceeded without completion or escalation, Temporal terminates the activity, marks task state as `FAILED`, and triggers the Failure Recovery Protocol.

---

## 6. Concurrency Control

To prevent conflicting file modifications:
- Only **one** agent may hold write permissions to a workspace at any given time.
- Read-only agents (Archaeologist, Reviewer, Test Engineer) may inspect workspaces concurrently under immutable snapshot mounts.
- Ghost Repairer requires an exclusive write lock on the target workspace before delegation can be fulfilled.
