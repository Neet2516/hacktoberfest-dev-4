# SPECTER Task Management System

> **SPECTER — The Ghost Maintainer**  
> Autonomous AI-powered code maintenance and repair system.

---

## Purpose

This `tasks/` directory is the **single source of truth** for all work items in the SPECTER project. It replaces ad-hoc issue trackers during initial development by providing:

- A git-native, reviewable task history
- Explicit agent-to-task assignment
- Dependency-aware scheduling
- Structured acceptance criteria for every deliverable

Every feature, infrastructure change, bug fix, and documentation item has a corresponding task file here. Tasks are the contract between the planning layer (humans, PRD) and the execution layer (agents, developers).

---

## Directory Structure

```
tasks/
├── README.md               ← You are here. System overview.
├── TASK_TEMPLATE.md        ← Master template for all task files
├── TASK_INDEX.md           ← Master index of all tasks (SPECTER-001…SPECTER-130)
├── DEPENDENCY_GRAPH.md     ← Visual dependency graph and critical path
│
├── backlog/                ← Tasks not yet scheduled for a sprint
│   └── SPECTER-NNN.md
│
├── ready/                  ← Dependencies met; ready to be picked up
│   └── SPECTER-NNN.md
│
├── in-progress/            ← Actively being worked on by an agent or human
│   └── SPECTER-NNN.md
│
├── review/                 ← Implementation complete; awaiting review/QA
│   └── SPECTER-NNN.md
│
├── blocked/                ← Stalled on an external dependency or decision
│   └── SPECTER-NNN.md
│
└── completed/              ← Done; all acceptance criteria met
    └── SPECTER-NNN.md
```

### Folder Semantics

| Folder | Meaning |
|--------|---------|
| `backlog/` | Defined but not yet ready — dependencies outstanding or not yet prioritized into a sprint |
| `ready/` | All dependencies satisfied; can be picked up immediately |
| `in-progress/` | An agent or human has claimed the task and is actively executing it |
| `review/` | Code/artifacts produced; waiting for Adversarial Reviewer agent or human sign-off |
| `blocked/` | Work has stalled due to an external blocker (decision needed, external API down, etc.) |
| `completed/` | All acceptance criteria checked, Definition of Done met, evidence attached |

---

## Task Lifecycle

```
                       ┌──────────┐
                       │ BACKLOG  │  ← Newly created tasks land here
                       └────┬─────┘
                            │ Dependencies met + sprint prioritized
                            ▼
                       ┌──────────┐
                       │  READY   │  ← Safe to start; all inputs available
                       └────┬─────┘
                            │ Agent/human picks up task
                            ▼
                      ┌─────────────┐
              ┌──────▶│ IN-PROGRESS │◀──────────────────────┐
              │       └──────┬──────┘                       │
              │              │ Blocker discovered            │
              │              ▼                              │
              │        ┌─────────┐                          │
              │        │ BLOCKED │  ← Moves back to         │
              │        └─────────┘    IN-PROGRESS when      │
              │              │        unblocked              │
              │              │ Implementation complete       │
              │              ▼                              │
              │        ┌──────────┐                         │
              │        │  REVIEW  │  ← Adversarial Reviewer │
              │        └────┬─────┘    or human reviews     │
              │             │ Review fails → corrections needed
              └─────────────┘
                            │ Review passes
                            ▼
                      ┌───────────┐
                      │ COMPLETED │  ← Evidence attached, task closed
                      └───────────┘
```

Moving a task between states = moving the `.md` file between folders + updating the `Current Status` field inside the file.

---

## How to Create a Task

1. Copy `tasks/TASK_TEMPLATE.md` to `tasks/backlog/SPECTER-NNN.md` where `NNN` is the next available sequential number (check `TASK_INDEX.md`).
2. Fill in **all 20 fields**. Do not leave any field blank — use `None` or `N/A` only when genuinely not applicable.
3. Add the task to `TASK_INDEX.md` (new row in the master table).
4. Update `DEPENDENCY_GRAPH.md` if the task creates new dependency edges.
5. Open a PR for the new task file — task creation is a code review event.

---

## Task ID Format

All tasks use the format **`SPECTER-NNN`** where `NNN` is a zero-padded three-digit integer starting at `001`.

Examples: `SPECTER-001`, `SPECTER-042`, `SPECTER-130`

Task IDs are **permanent** — they never change, even if a task is cancelled or superseded. Cancelled tasks are marked `CANCELLED` in their status field and remain in their last folder.

---

## Epic Groupings

Tasks are grouped into 18 epics corresponding to major system capabilities:

| Epic | Range | Theme |
|------|-------|-------|
| EPIC 01 | SPECTER-001–010 | Project Foundation |
| EPIC 02 | SPECTER-011–020 | Backend Infrastructure |
| EPIC 03 | SPECTER-021–027 | Repository Ingestion |
| EPIC 04 | SPECTER-028–034 | Repository Archaeology |
| EPIC 05 | SPECTER-035–041 | GitHub Integration |
| EPIC 06 | SPECTER-042–048 | AI Agent Runtime |
| EPIC 07 | SPECTER-049–054 | Agent-to-Agent Communication |
| EPIC 08 | SPECTER-055–061 | Ghost Memory |
| EPIC 09 | SPECTER-062–067 | Issue Investigation |
| EPIC 10 | SPECTER-068–073 | Autonomous Code Repair |
| EPIC 11 | SPECTER-074–079 | Adversarial Code Review |
| EPIC 12 | SPECTER-080–086 | Isolated Test Execution |
| EPIC 13 | SPECTER-087–093 | Durable Workflow Orchestration |
| EPIC 14 | SPECTER-094–099 | Human Approval and GitHub PR |
| EPIC 15 | SPECTER-100–110 | Frontend Dashboard |
| EPIC 16 | SPECTER-111–117 | Security and Threat Mitigation |
| EPIC 17 | SPECTER-118–124 | Observability and Testing |
| EPIC 18 | SPECTER-125–130 | Deployment and Documentation |

---

## Agent-to-Task Mapping

| Agent | Primary Task Responsibility |
|-------|-----------------------------|
| **Repository Archaeologist** | EPIC 04 (SPECTER-028–034) |
| **Issue Investigator** | EPIC 09 (SPECTER-062–067) |
| **Ghost Repairer** | EPIC 10 (SPECTER-068–073) |
| **Adversarial Reviewer** | EPIC 11 (SPECTER-074–079) |
| **Test Engineer** | EPIC 12 (SPECTER-080–086) |
| **Resurrection Coordinator** | EPIC 13 (SPECTER-087–093) |
| **Human/DevOps** | EPICs 01, 02, 08, 18 |
| **Frontend Developer** | EPIC 15 (SPECTER-100–110) |
| **Security Engineer** | EPIC 16 (SPECTER-111–117) |

---

## Priority Levels

| Level | Label | Meaning | Examples |
|-------|-------|---------|---------|
| **P0** | Critical | Blocks all other work; must be done first | Foundation setup, security gates |
| **P1** | High | Required for MVP; must be in first release | Core agents, Docker isolation, GitHub PR |
| **P2** | Medium | Important enhancement; targeted for v1.1 | Ghost Memory advanced features, observability |
| **P3** | Low | Post-MVP; planned but deferrable | Deployment automation, advanced UI polish |

P0 tasks failing = project cannot proceed. P3 tasks failing = project ships without that feature.

---

## Updating Task Status

When an agent transitions a task, it must:

1. Move the `.md` file to the appropriate folder.
2. Update the `## Current Status` field to the new state + timestamp.
3. If completing a task, fill in `## Evidence of Completion` with links to commits, PRs, or test logs.
4. If blocking a task, fill in `## Blockers` with a precise description and who/what must resolve it.

This ensures the task file is always self-describing, regardless of which agent or human reads it.
