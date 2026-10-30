import os

os.makedirs('agent/protocols', exist_ok=True)

message_protocol = """# SPECTER Message Protocol Specification

## 1. Purpose and Scope
The SPECTER Message Protocol defines the canonical wire-format, serialization rules, delivery semantics, and validation requirements for all inter-agent and system-to-agent communication across the SPECTER multi-agent system.

Unstructured or conversational-only communication between agents is strictly prohibited in automated execution paths. Every operational instruction, state change, intermediate finding, and handoff must be encapsulated within a verified `SpecterAgentMessage` conforming to `agent/schemas/agent-message.schema.json`.

---

## 2. Canonical Message Format

Every message exchanged across the SPECTER message bus must contain the following fields:

```json
{
  "message_id": "msg_01HJ8Z9X2B3C4D5E6F7G8H9J",
  "from": "issue_investigator",
  "to": "ghost_repairer",
  "task_id": "SPECTER-068",
  "message_type": "repair_specification",
  "payload": {
    "problem_statement": "Buffer underflow in config parser on empty input",
    "target_files": ["src/parser/config.rs"],
    "root_cause": "Unchecked subtraction on slice length when length is 0",
    "suggested_fix": "Add guard clause checking len() > 0 before indexing",
    "preservation_constraints": [
      "Preserve existing error enum ConfigError",
      "Do not modify public API of parse_config()"
    ]
  },
  "evidence_refs": [
    "git:commit:a1b2c3d4",
    "file:src/parser/config.rs#L45-L52",
    "test:crates/parser/tests/empty_input.rs"
  ],
  "timestamp": "2026-10-31T00:15:00.000Z",
  "execution_status": "ready",
  "schema_version": "1.0.0"
}
```

---

## 3. Field Specifications & Constraints

| Field | Type | Required | Description & Validation Rules |
|---|---|---|---|
| `message_id` | String | Yes | Unique identifier matching regex `^msg_[a-zA-Z0-9_-]+$`. Typically ULID or UUIDv4 with `msg_` prefix. |
| `from` | String | Yes | Identity of sender agent or supervisor. Must be in allowed registry: `resurrection_coordinator`, `repository_archaeologist`, `issue_investigator`, `ghost_repairer`, `adversarial_reviewer`, `test_engineer`, `human_supervisor`. |
| `to` | String | Yes | Recipient agent, `broadcast`, or `human_supervisor`. Must be in registry or `broadcast`. |
| `task_id` | String | Yes | Identifier of the task context matching `^(SPECTER-[0-9]{3}\|task_[a-zA-Z0-9_-]+)$`. |
| `message_type` | String | Yes | Functional type discriminator (see Section 4). |
| `payload` | Object | Yes | Strongly typed data payload associated with `message_type`. Must validate against type sub-schema. |
| `evidence_refs` | Array[String]| Yes | List of verifiable URIs, Git SHAs, file spans, or test IDs supporting the payload statements. |
| `timestamp` | String (ISO 8601)| Yes | UTC timestamp formatted as `YYYY-MM-DDTHH:MM:SS.sssZ`. |
| `execution_status`| String | Yes | Current state of task execution: `pending`, `in_progress`, `ready`, `completed`, `rejected`, `failed`, `blocked`. |
| `schema_version` | String | Yes | Semantic version of protocol, defaults to `1.0.0`. |

---

## 4. Message Type Taxonomy

1. `delegation`: Coordinator assigns a task to a specialized agent.
2. `acknowledgment`: Recipient acknowledges receipt and acceptance of delegation.
3. `repository_context`: Repository Archaeologist broadcasts or sends parsed context.
4. `investigation_report`: Issue Investigator delivers root cause and affected files.
5. `repair_specification`: Issue Investigator produces technical constraints for repair.
6. `patch_proposal`: Ghost Repairer submits candidate unified Git diff.
7. `review_verdict`: Adversarial Reviewer delivers verdict (`APPROVED`, `REQUEST_CHANGES`, `REJECTED_UNSAFE`).
8. `test_plan`: Test Engineer details container execution commands.
9. `verification_report`: Test Engineer reports containerized execution output and exit codes.
10. `approval_request`: Coordinator notifies human supervisor that human gate is reached.
11. `approval_response`: Human supervisor approves or rejects remote operation.
12. `escalation`: Agent or coordinator escalates an unresolvable issue or security tripwire.
13. `heartbeat`: Agent health signal emitted during long-running processing.
14. `error`: Explicit protocol error or unhandled exception notification.

---

## 5. Delivery Guarantees & Idempotency

1. **At-Least-Once Delivery**: Messages are published to PostgreSQL `agent_messages` table and routed via Temporal workflow signals.
2. **Idempotency Key**: The `message_id` serves as the primary deduplication key. Processing an identical `message_id` multiple times must result in a cached response without side effects.
3. **Ordering**: Sequence is strictly maintained within a single `task_id` workflow instance using Temporal's deterministic sequence numbers.
4. **Immutability**: Once written to the message repository, message records can never be updated or deleted. Corrections are made via new messages referencing the prior `message_id`.

---

## 6. Security and Sanitization Rules

- **Zero Secret Transmission**: Under no circumstances may GitHub tokens, API keys, or private key material be serialized in any message field.
- **Untrusted Content Encapsulation**: Repository content extracted from untrusted codebases must be placed in designated data fields and never concatenated into execution instructions.
- **Validation Before Ingestion**: The receiving agent runtime must run JSON schema validation prior to unmarshaling or executing on any incoming message. Messages failing schema validation trigger an immediate `error` response and do not transition task state.
"""

delegation_protocol = """# SPECTER Task Delegation Protocol

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
"""

handoff_protocol = """# SPECTER Sequential Handoff Protocol

## 1. Pipeline Sequence
SPECTER's core maintenance pipeline executes sequentially across specialized agents:

1. **Repository Archaeologist** $\\rightarrow$ Repository Context Report
2. **Issue Investigator** $\\rightarrow$ Issue Reproduction & Repair Specification
3. **Ghost Repairer** $\\rightarrow$ Candidate Git Patch
4. **Adversarial Reviewer** $\\rightarrow$ Adversarial Review Verdict
5. **Test Engineer** $\\rightarrow$ Containerized Verification Report
6. **Resurrection Coordinator** $\\rightarrow$ Human Approval Proposal

---

## 2. Handoff Integrity Contracts

At each pipeline transition, the output of the upstream agent becomes the immutable input of the downstream agent. The Coordinator acts as the intermediary gatekeeper: direct point-to-point unmediated transfers without Coordinator registration are strictly prohibited.

### Transition 1: Archaeologist to Investigator
- **Input Artifact**: `Repository Context Report`
- **Integrity Check**:
  - Tree-sitter parse summary valid.
  - Core programming languages and dependency managers identified.
  - Target files verified to exist in repository Git tree.

### Transition 2: Investigator to Repairer
- **Input Artifact**: `Repair Specification`
- **Integrity Check**:
  - Exact target file paths identified and within permitted scopes.
  - Root cause articulated with reproduction evidence.
  - Preservation constraints clearly specified (e.g. no breaking public APIs).

### Transition 3: Repairer to Reviewer
- **Input Artifact**: `Candidate Git Patch` (Unified Diff)
- **Integrity Check**:
  - Valid unified diff format (`diff --git a/... b/...`).
  - Patch applies cleanly to target workspace baseline commit (`git apply --check`).
  - No out-of-scope files touched (e.g. CI files, secrets, dependency lockfile changes unless authorized).
  - Minimal line change threshold satisfied (no unrelated refactoring).

### Transition 4: Reviewer to Test Engineer
- **Input Artifact**: `Review Verdict`
- **Condition**: Only if `verdict == "APPROVED"`.
- **Integrity Check**:
  - Adversarial Reviewer confirmed no high/critical regression risks.
  - No security policy violations detected in patch diff.
  - *If verdict is `REQUEST_CHANGES`*, the Coordinator bounces the task back to Ghost Repairer with `findings` and decrements retry budget.

### Transition 5: Test Engineer to Coordinator (Approval Gate)
- **Input Artifact**: `Verification Report`
- **Condition**: All tests passing or delta test suite passes without regressions.
- **Integrity Check**:
  - Container executed with network disabled (`network: none`).
  - Container exited with code `0`.
  - Full container stdout/stderr captured in evidence archive.

---

## 3. Rejection & Bounce-Back Protocol

When an agent's output fails review or testing:
1. The rejecting agent generates an `agent-output` containing structured findings, line numbers, and corrective hints.
2. The Coordinator logs the rejection event in `memory/EXECUTION_STATE.md` and records attempt count.
3. If `attempt_count <= 3`:
   - Coordinator issues a new `delegation` to Ghost Repairer containing the prior patch, review findings, and test failures.
   - Ghost Repairer generates a revised minimal patch.
4. If `attempt_count > 3`:
   - Task is automatically transitioned to `BLOCKED`.
   - An `escalation` message is dispatched to the human supervisor.
"""

approval_protocol = """# SPECTER Human Approval Protocol

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
"""

escalation_protocol = """# SPECTER Escalation Protocol

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
"""

files = {
    'agent/protocols/MESSAGE_PROTOCOL.md': message_protocol,
    'agent/protocols/DELEGATION_PROTOCOL.md': delegation_protocol,
    'agent/protocols/HANDOFF_PROTOCOL.md': handoff_protocol,
    'agent/protocols/APPROVAL_PROTOCOL.md': approval_protocol,
    'agent/protocols/ESCALATION_PROTOCOL.md': escalation_protocol
}

for path, content in files.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created {path}")

print("All 5 protocol files written successfully.")

