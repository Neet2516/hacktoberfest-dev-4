# SPECTER Message Protocol Specification

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
