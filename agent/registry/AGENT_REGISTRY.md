# SPECTER Agent Registry

**Version:** 1.0.0
**Last Updated:** 2024-01-01
**Maintainer:** SPECTER Core Team

---

## Registry Overview

This document is the authoritative registry of all agents in the SPECTER system. Each agent entry includes its canonical identifier, current implementation status, role, and ownership.

**Status Definitions:**
- `defined` — Role documented; implementation not started
- `implemented` — Code written; not yet integration-tested
- `verified` — Integration-tested; running in production

---

## Agent Registry Table

| Agent ID | Name | Version | Status | Owner | Description |
|----------|------|---------|--------|-------|-------------|
| `agent:coordinator:v1` | Resurrection Coordinator | 1.0.0 | `defined` | Core Team | Orchestrates the full repair pipeline; manages task state machine; enforces quality gates; communicates with humans; the sole agent that can create PRs. |
| `agent:archaeologist:v1` | Repository Archaeologist | 1.0.0 | `defined` | Core Team | Performs deep structural analysis of a repository; builds a semantic map of files, dependencies, and code structure; generates pgvector embeddings for downstream semantic search. |
| `agent:investigator:v1` | Issue Investigator | 1.0.0 | `defined` | Core Team | Analyzes GitHub issues in the context of the repository map; identifies root causes; localizes affected code; produces investigation reports with evidence and confidence scores. |
| `agent:repairer:v1` | Ghost Repairer | 1.0.0 | `defined` | Core Team | Generates minimal, targeted code patches to resolve identified issues; validates patches for syntax correctness; preserves repository architecture and coding style. |
| `agent:reviewer:v1` | Adversarial Reviewer | 1.0.0 | `defined` | Core Team | Adversarially challenges proposed patches; identifies regressions, security risks, and correctness issues; provides verdict (APPROVED / REJECTED / NEEDS_HUMAN_REVIEW). |
| `agent:test-engineer:v1` | Test Engineer | 1.0.0 | `defined` | Core Team | Executes existing test suites against patched code inside isolated Docker containers; reports pass/fail results with evidence; never executes code on the host. |

---

## Agent ID Scheme

Agent IDs follow the format: `agent:<role>:v<major>`

- `<role>` — kebab-case role name (coordinator, archaeologist, investigator, repairer, reviewer, test-engineer)
- `v<major>` — major version; incremented only on breaking changes to message contract or capability set

Minor versions are tracked in the agent implementation codebase, not in this registry.

---

## Status Transition Policy

```
defined ──► implemented ──► verified
```

- `defined → implemented`: Requires passing unit tests and code review
- `implemented → verified`: Requires passing SPECTER integration test suite (all 6 agents tested together)
- Regression to a prior status is allowed when a breaking change is introduced
- Status changes must be reflected in this registry within 48 hours of the code change

---

## Agent Versioning Policy

- **Patch versions** (1.0.x): Bug fixes; no registry update required
- **Minor versions** (1.x.0): New capabilities added; update `AGENT_CAPABILITIES.md`; registry entry updated if contract changes
- **Major versions** (x.0.0): Breaking changes to message format, tool contract, or capability set; new registry entry; old entry marked `deprecated`; migration plan required

---

## Deprecated Agents

*(None at this time)*

---

## Notes

- All agents run as Temporal workflow activities within the `specter-agents` task queue
- Agent code lives in `agent/src/<role>/` within the SPECTER repository
- Each agent's system prompt is in `agent/prompts/SYSTEM_PROMPTS.md`
- Each agent's full role specification is in `agent/roles/<ROLE>.md`
