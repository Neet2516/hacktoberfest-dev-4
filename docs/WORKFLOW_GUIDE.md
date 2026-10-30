# SPECTER — Workflow Guide

> **Document Status:** Planning Phase — Not Yet Implemented  
> **Version:** 0.1.0  
> **Last Updated:** 2026-10-31  
> **Audience:** Developers, operators, and demo reviewers

---

## Table of Contents

1. [Onboarding a New Repository](#1-onboarding-a-new-repository)
2. [Running Repository Archaeology](#2-running-repository-archaeology)
3. [Selecting and Investigating an Issue](#3-selecting-and-investigating-an-issue)
4. [Ghost Repairer Cycle](#4-ghost-repairer-cycle)
5. [Adversarial Review Cycle](#5-adversarial-review-cycle)
6. [Test Execution in Docker](#6-test-execution-in-docker)
7. [Human Approval and PR Creation](#7-human-approval-and-pr-creation)
8. [Failure Recovery](#8-failure-recovery)
9. [Querying Ghost Memory](#9-querying-ghost-memory)
10. [Demo Scenario Walkthrough](#10-demo-scenario-walkthrough)
11. [State Machine Diagrams](#11-state-machine-diagrams)
12. [Example Outputs](#12-example-outputs)

---

## 1. Onboarding a New Repository

### Purpose
Register a public GitHub repository with SPECTER so that it can be analyzed, maintained, and have pull requests created on its behalf.

### Prerequisites
- A running SPECTER instance (local Docker Compose or deployed)
- The public URL of the GitHub repository (must be `https://github.com/owner/repo`)
- A GitHub Personal Access Token (PAT) with the following scopes:
  - `repo` (for reading issues and creating PRs/branches)
  - `read:user` (optional, for identifying the token owner)

### Step-by-Step

**Step 1 — Open SPECTER**

Navigate to `http://localhost:3000` (local) or the deployed URL. You will see the landing page with a repository input form.

**Step 2 — Enter the Repository URL**

Paste the GitHub repository URL into the "Repository URL" field. Example:
```
https://github.com/pallets/flask
```

**Step 3 — Provide a GitHub Token**

Paste your PAT into the "GitHub Token" field. This field is masked (password input). The token is transmitted over HTTPS and stored only in the server's in-memory vault for the duration of your session.

> **Security Note:** The token is never written to disk, logs, or the database. It is never sent to the LLM. It is used exclusively for GitHub API calls.

**Step 4 — Submit**

Click **"Analyze Repository"**. The following happens:
- The frontend sends `POST /api/v1/repositories` with the URL and token
- The API validates the URL (must be `github.com`, `https` only)
- The API verifies the repository exists via the GitHub API
- The API stores the repository metadata and starts the Temporal workflow
- You are redirected to the repository dashboard: `/repos/{repo_id}`

**Expected UI State After Step 4:**

The repository dashboard appears with:
- Repository name and description (fetched from GitHub)
- Status badge: `ARCHAEOLOGY IN PROGRESS`
- React Flow agent graph: Archaeologist node is highlighted/pulsing
- Live log stream showing cloning progress

**Expected Duration:** Repository cloning takes 10–90 seconds depending on repository size. Archaeology takes 5–30 minutes depending on codebase size and LLM speed.

**API Call:**
```http
POST /api/v1/repositories
Authorization: Bearer <session-jwt>
Content-Type: application/json

{
  "github_url": "https://github.com/pallets/flask",
  "github_token": "ghp_xxxx"
}
```

**Response (201 Created):**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "github_url": "https://github.com/pallets/flask",
  "owner": "pallets",
  "repo_name": "flask",
  "status": "archaeology",
  "created_at": "2026-10-31T12:00:00Z"
}
```

---

## 2. Running Repository Archaeology

### Purpose
The Repository Archaeologist reconstructs the history, architecture, and purpose of the repository. This is always the first automated step after cloning.

### What the Agent Does

1. **Directory Structure Analysis**
   - Walks the entire directory tree
   - Identifies entry points (`main.py`, `index.js`, `Cargo.toml`, etc.)
   - Detects programming languages and their file counts
   - Maps top-level modules and packages

2. **Configuration File Inspection**
   - Reads `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`
   - Parses build system files (`package.json`, `pyproject.toml`, `Cargo.toml`, `Makefile`)
   - Reads CI configuration (`.github/workflows`, `.travis.yml`, etc.)

3. **Git History Analysis**
   - Retrieves the last 200 commits (configurable)
   - Identifies the most frequently changed files ("hot files")
   - Identifies key contributors and their focus areas
   - Finds commits with keywords: `fix`, `bug`, `revert`, `breaking` (architectural decision signals)
   - Traces the origin of major modules (first commit introducing each top-level directory)

4. **AST Symbol Extraction (Tree-sitter)**
   - Builds a symbol map: all public functions, classes, interfaces
   - Constructs an import dependency graph
   - Identifies circular dependencies

5. **LLM Analysis**
   - Feeds the above data to Gemma as `<context>`
   - Asks Gemma to:
     - Describe the repository's purpose in 2–3 sentences
     - Identify the primary architectural pattern (MVC, event-driven, microservices, etc.)
     - List the 5 most important modules and their roles
     - Identify any likely architectural decisions baked into the code
     - Flag any obvious technical debt markers

6. **Ghost Memory Population**
   - Writes memory entries for:
     - Architectural decisions (category: `architectural_decision`)
     - Hot files and their roles (category: `architectural_decision`)
     - Known broken dependencies detected in lockfiles (category: `known_broken_dependency`)
     - Any issues referenced in commit messages (category: `unresolved_issue`)

### Expected Duration

| Repository Size | Expected Duration |
|---|---|
| < 1,000 files | 5–10 minutes |
| 1,000–5,000 files | 10–20 minutes |
| 5,000+ files | 20–30 minutes |

### Output Format: Repository Context Report

See [Section 12.1](#121-example-repository-context-report) for a full example.

The report is stored in the `ghost_memory` table and displayed in the repository dashboard under the "Context" tab.

---

## 3. Selecting and Investigating an Issue

### Purpose
After archaeology is complete, the user selects a GitHub issue for SPECTER to investigate and repair.

### Selecting an Issue

**Step 1 — View Issues**

In the repository dashboard, click the **"Issues"** tab. SPECTER fetches the open issues from GitHub and displays them in a list with:
- Issue number and title
- Labels
- Created date
- Comment count
- Estimated complexity (Low / Medium / High — heuristic from issue body length and label keywords)

**Step 2 — Select an Issue**

Click any issue to view its full body and comments. When ready, click **"Investigate This Issue"**.

**Step 3 — Investigation Begins**

The API call:
```http
POST /api/v1/repositories/{repo_id}/tasks
Authorization: Bearer <session-jwt>
Content-Type: application/json

{
  "issue_number": 42
}
```

The Temporal workflow receives the issue number. The Issue Investigator agent begins.

### What the Issue Investigator Does

1. **Issue Analysis**
   - Reads the issue title, body, and comments
   - Extracts: error messages, file paths, function names, expected vs. actual behavior

2. **Ghost Memory Query**
   - Searches memory for related historical bugs and previously rejected approaches
   - Searches for knowledge about the affected files

3. **Code Localization**
   - Uses Tree-sitter to find the functions/classes mentioned in the issue
   - Traces call chains: which callers reach the reported function?
   - Identifies the commit that last modified the affected code

4. **Root Cause Determination**
   - Feeds localized code + issue text to Gemma
   - Gemma proposes 2–3 possible root causes, ranked by likelihood

5. **Repair Specification Generation**
   - Selects the highest-confidence root cause
   - Produces a structured Repair Specification:
     - Affected files and line ranges
     - Proposed action (what to change and why)
     - Expected outcome
     - Constraints (what must NOT be changed)

### Output Format: Investigation Report

See [Section 12.2](#122-example-investigation-report) for a full example.

### Expected Duration

| Issue Complexity | Expected Duration |
|---|---|
| Simple (1 file, clear error) | 3–8 minutes |
| Medium (2–5 files, traceable) | 8–15 minutes |
| Complex (many files, indirect) | 15–20 minutes |

---

## 4. Ghost Repairer Cycle

### Purpose
The Ghost Repairer implements the Repair Specification produced by the Issue Investigator, generating a minimal, targeted code patch.

### Inputs
- Investigation Report (from Issue Investigator)
- Repair Specification (structured)
- Ghost Memory (rejected approaches, previous verified patches)

### Repair Process

1. **Read Relevant Memory**
   - Query Ghost Memory for previously rejected approaches related to the affected files
   - Read verified patches from related historical fixes

2. **Code Understanding**
   - Run Tree-sitter on the affected files to understand their structure
   - Identify the exact function/block to change

3. **Patch Generation**
   - Call Gemma with:
     - The exact affected code block as `<context>`
     - The repair specification as the task description
     - An explicit instruction to generate a unified diff patch
     - A constraint: "Do not modify any file not listed in the affected_files list"

4. **Patch Validation**
   - Parse the generated diff with `python-patch` library
   - Verify all targeted file paths exist in the workspace
   - Apply the patch to a temporary copy: `git apply --check specter.patch`
   - Run Tree-sitter on the patched files to verify syntactic validity

5. **Output**
   - Write the validated patch to `/workspace/{repo_id}/specter.patch`
   - Send `AgentMessage(PROPOSED_PATCH)` to the Adversarial Reviewer

### Approval Gate Within the Repairer Cycle

The Ghost Repairer does **not** have an internal human approval gate. It produces a patch and sends it to the Reviewer. Only after the full Reviewer + Test cycle does the human approval gate appear.

### Rejection and Retry

If the Adversarial Reviewer rejects the patch:
1. The Reviewer sends `AgentMessage(CORRECTION_REQUEST)` back to the Repairer
2. The Repairer reads the correction request
3. A new repair iteration begins (max 3 iterations total)
4. If 3 iterations all fail review, the task is marked `failed` and a human-readable explanation is provided

---

## 5. Adversarial Review Cycle

### Purpose
The Adversarial Reviewer independently inspects the proposed patch — without the Repairer's context — and either accepts, conditionally accepts, or rejects it.

### Key Design Principle

The Reviewer **does not receive the Repairer's reasoning**. It sees only:
- The patch diff
- The original issue description
- The Ghost Memory (shared knowledge)

This simulates an independent code review and prevents the Reviewer from being anchored to the Repairer's assumptions.

### Review Process

1. **Read Patch**
   - Parse the unified diff
   - Apply patch to a temporary copy for AST analysis

2. **Independent Analysis**
   - Run Tree-sitter on pre-patch and post-patch versions
   - Detect: public API changes, new unchecked error paths, removed null guards, type changes

3. **Security Check**
   - Scan patch for: hardcoded credentials, `eval()` calls, unsafe deserialisation, network calls, file system writes outside expected paths

4. **LLM Critique (Independent Context)**
   - Separate Ollama call with no Repairer output in context
   - Ask Gemma to identify:
     - Does this patch actually fix the reported issue?
     - Could it cause regressions in related functionality?
     - Are there edge cases not handled?
     - Are there simpler ways to achieve the same fix?

5. **Verdict**
   - `accepted`: Patch passes all checks. Forward to Test Engineer.
   - `conditional`: Patch is mostly correct but needs minor modifications. Repairer given specific corrections.
   - `rejected`: Patch fails a critical check. Detailed rejection reason sent to Repairer.

### Output Format: Review Verdict

See [Section 12.3](#123-example-review-verdict) for a full example.

### Demo Injection Point

For the Hacktoberfest demo, a deliberately faulty patch can be submitted first to demonstrate the Reviewer rejecting it. The workflow for this is:
1. Configure the Ghost Repairer to use the `faulty_patch` fixture (pre-built patch with an intentional bug)
2. The Adversarial Reviewer detects the bug and rejects it
3. The Repairer generates the correct patch on iteration 2
4. The Reviewer accepts iteration 2

---

## 6. Test Execution in Docker

### Purpose
The Test Engineer discovers the repository's test framework, executes the relevant tests against the patched code in an isolated Docker container, and reports pass/fail results.

### Container Setup

1. **Language Detection** — identify repository language from file extensions
2. **Base Image Selection:**

| Language | Base Image |
|---|---|
| Python | `python:3.12-slim` |
| Node.js / TypeScript | `node:22-slim` |
| Rust | `rust:1.82-slim` |
| Go | `golang:1.23-slim` |
| Java | `eclipse-temurin:21-slim` |
| Ruby | `ruby:3.3-slim` |
| Unknown | `ubuntu:24.04` |

3. **Test Framework Detection:**

| Framework | Detection Signal |
|---|---|
| pytest | `pyproject.toml` has `[tool.pytest]` or `tests/` dir with `conftest.py` |
| Jest | `package.json` has `"test": "jest"` |
| Mocha | `package.json` has `"test": "mocha"` |
| Cargo test | `Cargo.toml` present |
| Go test | `*_test.go` files present |
| RSpec | `spec/` dir with `spec_helper.rb` |

4. **Test Command Construction:**

| Framework | Command |
|---|---|
| pytest | `python -m pytest tests/ -v --tb=short` |
| Jest | `npm test -- --forceExit` |
| Cargo test | `cargo test 2>&1` |
| Go test | `go test ./... -v` |
| RSpec | `bundle exec rspec` |

### Container Execution

```
Docker Create:
  Image: <detected base image>
  Volumes: /workspace/{repo_id} → /workspace:ro
  Network: none
  CPU: 2.0
  Memory: 2GB
  PidsLimit: 256
  ReadonlyRootfs: true
  Tmpfs: /tmp:size=512m
  Environment: (none from host)
  Command: /bin/sh -c "cp -r /workspace /tmp/work && cd /tmp/work && <patch apply> && <test command>"

Docker Start → Stream stdout/stderr → Capture exit code → Docker Remove
```

### Result Interpretation

| Exit Code | Meaning |
|---|---|
| 0 | All tests passed |
| 1 | Some tests failed |
| 2 | Test framework configuration error |
| 124 | Timeout (killed after 10 minutes) |
| 125+ | Container runtime error |

The Test Engineer parses test output to extract:
- Total tests run
- Tests passed
- Tests failed
- Tests errored
- Specific failure messages

### Output Format: Verification Report

See [Section 12.4](#124-example-verification-report) for a full example.

---

## 7. Human Approval and PR Creation

### Purpose
After all agents have completed their work, SPECTER presents the human with a complete picture of the proposed change and waits for explicit approval before touching the remote repository.

### What the Approval Gate Shows

The approval gate page (`/approval/{task_id}`) displays:

**Section 1 — Issue Summary**
- Issue number, title, and body
- Link to original GitHub issue

**Section 2 — Proposed Patch**
- Unified diff view (syntax-highlighted, line-by-line)
- Files changed, lines added, lines removed

**Section 3 — Review Verdict**
- Verdict: ACCEPTED / CONDITIONAL
- Reviewer's critique (full text)
- Any security observations
- Regression risk assessment

**Section 4 — Test Results**
- Test framework detected
- Total / Passed / Failed counts
- Failed test names (if any)
- Link to full test output (expandable)

**Section 5 — Ghost Memory Insights**
- Memory entries referenced during this task
- Previously rejected approaches (so you know what was considered)

**Section 6 — Maintenance Report Preview**
- Preview of the PR description that will be created

**Approval Actions:**

| Action | Effect |
|---|---|
| **Approve & Create PR** | Sends `approve_task` signal to Temporal; PR creation begins |
| **Reject** | Sends `reject_task` signal; task marked cancelled; no remote changes |
| **Download Patch** | Downloads `specter.patch` file for manual application |

### PR Creation

After approval:

1. GitHub API: Create branch `specter/{task_id}` from `{default_branch}`
2. Git: Apply patch and commit with message:
   ```
   fix: {issue_title} (SPECTER #{task_id[:8]})

   Closes #{issue_number}
   ```
3. GitHub API: Create PR with:
   - Title: `fix: {issue_title}` 
   - Body: Full Maintenance Report (see Section 12.5)
   - Base: `{default_branch}`
   - Head: `specter/{task_id}`
   - Draft: false
   - Labels: `specter-generated`

4. PR URL stored in `approvals.pr_url`
5. Frontend displays PR link

---

## 8. Failure Recovery

### How SPECTER Handles Failures

SPECTER uses Temporal for durable workflow execution. Every activity (agent run) is a checkpointed step. If any worker crashes:

1. Temporal detects the activity heartbeat timeout
2. Temporal reschedules the activity on the next available worker
3. The activity re-runs from its start (activities are designed to be idempotent)
4. The workflow continues from the last successful checkpoint

### What State Is Preserved

| State Item | Storage | Recovery Mechanism |
|---|---|---|
| Workflow stage | Temporal event history | Automatic — Temporal replays history |
| Agent messages | `agent_messages` table (PostgreSQL) | Coordinator reads unprocessed messages on startup |
| Ghost Memory entries | `ghost_memory` table (PostgreSQL) | Persisted across restarts |
| Patches | `patches` table (PostgreSQL) | Repairer checks for existing patch before regenerating |
| Workspace files | Docker volume `specter_workspaces` | Volume persists across container restarts |
| GitHub token | Rust in-memory vault | **NOT** persisted — user must re-enter if server restarts |

### How to Resume a Failed Task

**Scenario A: Agent worker crashed mid-activity**

No action required. Temporal will automatically reschedule the activity within the retry policy timeout. Refresh the task dashboard to see the current status.

**Scenario B: Rust API server restarted**

If the user's session JWT is still valid (< 1 hour), they can continue by re-navigating to `/repos/{repo_id}`. If the GitHub token was in the vault and the server restarted, the user must re-enter their token via `PATCH /api/v1/repositories/{repo_id}/token`.

**Scenario C: Task stuck in `failed` state**

Navigate to the task dashboard. Click **"Retry Task"** (which sends a `retry_task` signal to the Temporal workflow). The workflow resumes from the last successful checkpoint.

**Scenario D: Temporal server restarted**

Temporal is stateful. If using the Docker Compose setup, Temporal's state is persisted in PostgreSQL. Restarting `docker-compose up temporal` restores all workflow histories.

### Idempotency in Activities

Each activity checks for existing output before running:
- `clone_repository`: If the workspace directory exists and is a valid git repo, skip clone
- `run_archaeologist`: If a `repository_context` message already exists for this task, return it
- `run_ghost_repairer`: If a patch for this iteration already exists in the `patches` table, return it
- `create_pull_request`: If a PR URL exists in `approvals`, return it (don't create a duplicate)

---

## 9. Querying Ghost Memory

### What Ghost Memory Contains

Ghost Memory is SPECTER's persistent, per-repository knowledge base. It stores:

| Category | Description | Examples |
|---|---|---|
| `architectural_decision` | How the codebase is structured | "Uses Flask blueprints for routing", "All database calls go through the Repository pattern" |
| `historical_bug_fix` | Past bug repairs (from git history analysis) | "Commit abc123 fixed null pointer in user auth flow" |
| `rejected_approach` | Approaches that were tried and failed | "Adding a try-catch here broke the event loop" |
| `known_broken_dependency` | Dependencies known to have issues | "requests==2.25.0 has a known CVE affecting redirect handling" |
| `unresolved_issue` | Open issues referenced in commits | "Issue #42 (null handling in parser) still open as of HEAD" |
| `investigation_report` | Full investigation outputs | Stored after each Issue Investigator run |
| `verified_patch` | Patches that passed review and tests | Stored after each successful Test Engineer run |

### Reading Memory via the UI

1. Navigate to `/repos/{repo_id}/memory`
2. Use the category filter (dropdown) to filter by memory category
3. Use the search bar (performs semantic vector similarity search)
4. Click any memory entry to see:
   - Full content
   - Confidence level (fact / hypothesis / speculation)
   - Source reference (commit SHA, issue URL, or file path)
   - Created by (which agent created this entry)
   - Created at (timestamp)
   - Whether it has been superseded by a newer entry

### Reading Memory via the API

```http
GET /api/v1/repositories/{repo_id}/memory?category=architectural_decision&query=authentication+flow&limit=10
Authorization: Bearer <session-jwt>
```

Response:
```json
{
  "entries": [
    {
      "id": "uuid",
      "category": "architectural_decision",
      "content": "Authentication is handled via Flask-Login with session cookies...",
      "source_ref": "src/auth/login.py",
      "confidence": "fact",
      "similarity": 0.91,
      "created_by": "archaeologist",
      "created_at": "2026-10-31T12:00:00Z"
    }
  ]
}
```

### Memory Confidence Levels

| Level | Meaning |
|---|---|
| `fact` | Derived from Git history, file contents, or verified test output — objectively verifiable |
| `hypothesis` | Generated by LLM analysis — plausible but not verified by execution |
| `speculation` | Low-confidence LLM guess — marked for human review |

---

## 10. Demo Scenario Walkthrough

This walkthrough follows the Hacktoberfest demo scenario from PRD Section 15.

### Target Repository (Recommended)

Select a small, well-known open-source repository with:
- At least 50 open issues
- A clear, reproducible bug report with an error traceback
- A test suite (pytest, jest, or cargo test)
- Python, JavaScript/TypeScript, or Rust codebase (best Tree-sitter support)

**Suggested candidates** (to be confirmed — see BLOCKERS.md BLK-019):
- `pallets/flask` (Python, well-tested, active issues)
- `lukeed/kleur` (Node.js, tiny, easy to demonstrate)
- A purpose-built fixture repository with guaranteed reproducibility

### Demo Steps

**Step 1 — Repository Submission (2 minutes)**

Live action: Open SPECTER at `http://localhost:3000`. Paste the demo repository URL. Paste the GitHub token. Click Analyze.

Talking point: "SPECTER clones the repository into an isolated workspace. Note that the GitHub token never leaves the server's memory."

**Step 2 — Archaeology (5–10 minutes, can pre-run)**

Live action: Show the repository dashboard. The Archaeologist node pulses. Logs stream in: "Analyzing directory structure...", "Running Tree-sitter on 47 files...", "Querying Git history (200 commits)...". After completion, show the Repository Context Report.

Talking point: "The Archaeologist reconstructed the architecture without reading any documentation. It identified the primary design patterns from code and history alone."

**Step 3 — Issue Selection (1 minute)**

Live action: Click the Issues tab. Select a real open issue — e.g., "NullPointerException when parsing empty input". Click "Investigate This Issue".

Talking point: "This is a real open issue that has been unresolved for 6 months. Let's see if SPECTER can crack it."

**Step 4 — Investigation (5 minutes)**

Live action: Show the Issue Investigator node becoming active. The log shows: "Searching Ghost Memory for related entries...", "Locating affected symbols via Tree-sitter...", "Tracing call chain...". After completion, show the Investigation Report with the identified root cause.

Talking point: "The Investigator found the bug in `src/utils/parser.ts` line 47 — a missing null guard before an array index access."

**Step 5 — Faulty Patch Injection (demo mode)**

The Ghost Repairer generates the first patch — pre-configured to be the fixture faulty patch (adds a null guard but also accidentally changes a function signature).

**Step 6 — Adversarial Review Rejection (2 minutes)**

Live action: Show the Adversarial Reviewer node becoming active. After review, the Review Verdict appears: **REJECTED**. The reason: "The patch modifies the public signature of `parseInput()`, which is called by 12 other modules. This is a regression risk."

Talking point: "The Reviewer caught a mistake the Repairer made — without being told what the Repairer was thinking. This is independent adversarial review."

**Step 7 — Corrected Patch (3 minutes)**

Live action: Show the Repairer node activating again. It receives the correction request: "Do not change the function signature. Add the null guard inside the function body only." The second patch is generated and accepted by the Reviewer.

**Step 8 — Test Execution (3–5 minutes)**

Live action: Show a Docker container being created. The Test Engineer runs pytest inside the container. A terminal-style output streams in. All tests pass.

Talking point: "The tests ran inside a completely isolated container with no network access. The test container cannot reach the internet, cannot access our host filesystem, and is deleted after the tests complete."

**Step 9 — Human Approval (1 minute)**

Live action: Show the Approval Gate. Review the diff, the review verdict, and the test results. Click "Approve & Create PR".

Talking point: "SPECTER never merges autonomously. A human must review and approve every proposed change."

**Step 10 — Pull Request Created**

Live action: A GitHub PR link appears. Click it. The PR is live on GitHub with the full maintenance report in the description.

Talking point: "The pull request includes the full context — the investigation, the review, and the test results — so the human maintainer has everything they need to make an informed decision."

---

## 11. State Machine Diagrams

### 11.1 Repository State Machine

```
[REGISTERED]
     │
     │ (Temporal workflow starts)
     ▼
[CLONING]
     │
     │ (clone success)
     ▼
[ARCHAEOLOGY]
     │
     │ (archaeologist complete)
     ▼
[READY]
     │
     │ (task created)
     ▼
[TASK_ACTIVE] ──────────────────────────── (task failed → [TASK_FAILED])
     │
     │ (all tasks complete)
     ▼
[READY] (returns to ready for next task)
```

### 11.2 Task State Machine

```
[PENDING]
     │
     │ (workflow activity starts)
     ▼
[ARCHAEOLOGY] → [INVESTIGATING] → [REPAIRING] → [REVIEWING]
                                       ▲               │
                                       │   (rejected)  │
                                       └───────────────┘
                                                       │
                                                       │ (accepted)
                                                       ▼
                                               [TESTING]
                                                   │
                                                   │ (tests complete)
                                                   ▼
                                        [AWAITING_APPROVAL]
                                            │          │
                                    (approved)    (rejected)
                                            │          │
                                            ▼          ▼
                                   [CREATING_PR]  [CANCELLED]
                                            │
                                            │ (PR created)
                                            ▼
                                      [COMPLETED]

Any state → [FAILED] on unrecoverable error
[FAILED] → [REPAIRING] on manual retry
```

### 11.3 Workflow State Machine (Temporal)

```
WorkflowStarted
     │
     ├── Activity: clone_repository
     │       RetryPolicy: max 3 attempts, exponential backoff
     │
     ├── Activity: run_archaeologist
     │       RetryPolicy: max 2 attempts, linear backoff
     │
     ├── Activity: run_issue_investigator
     │       RetryPolicy: max 2 attempts
     │
     ├── Activity: run_ghost_repairer (iteration 1)
     │
     ├── Activity: run_adversarial_reviewer
     │       ├── If ACCEPTED: → run_test_engineer
     │       └── If REJECTED: → run_ghost_repairer (iteration 2)
     │               └── run_adversarial_reviewer (iteration 2)
     │                       ├── If ACCEPTED: → run_test_engineer
     │                       └── If REJECTED: → run_ghost_repairer (iteration 3)
     │                               └── run_adversarial_reviewer (iteration 3)
     │                                       ├── If ACCEPTED: → run_test_engineer
     │                                       └── If REJECTED: → WorkflowFailed
     │
     ├── Activity: run_test_engineer
     │
     ├── WaitForSignal: approve_task / reject_task (no timeout — human-controlled)
     │
     ├── [if approved] Activity: create_pull_request
     │
     └── WorkflowCompleted
```

---

## 12. Example Outputs

### 12.1 Example Repository Context Report

```markdown
# Repository Context Report
**Repository:** pallets/flask
**Generated by:** Repository Archaeologist
**Date:** 2026-10-31T12:00:00Z
**Confidence:** fact (from Git history and file analysis)

## Purpose
Flask is a lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications. It provides request routing, template rendering (via Jinja2), and a development server.

## Architecture Pattern
Layered monolith with pluggable extension system. Core concerns are separated into: routing (url_map), request/response lifecycle (ctx.py), and configuration. Extensions attach to the app object at initialization time (app.extensions dict).

## Primary Modules
| Module | Role |
|---|---|
| `src/flask/app.py` | Central Flask application class; route registration, extension management |
| `src/flask/routing.py` | URL rule matching (delegates to Werkzeug's routing) |
| `src/flask/ctx.py` | Request and application context management |
| `src/flask/templating.py` | Jinja2 integration and template rendering |
| `src/flask/testing.py` | Test client for unit testing Flask apps |

## Key Architectural Decisions
1. Delegates routing entirely to Werkzeug — Flask is a thin layer on top.
2. Context variables (g, request) use thread-local / greenlet-local storage.
3. Extension pattern: extensions modify the app at `init_app()` time.
4. No built-in ORM or database integration by design — delegated to extensions.

## Technical Debt Markers
- `src/flask/globals.py`: Thread-local usage with a note about async compatibility concerns
- `CHANGES.rst`: 14 known deprecation warnings present in 3.1.x

## Ghost Memory Entries Written
- 6 architectural_decision entries
- 3 known_broken_dependency entries (from requirements/*.txt lockfiles)
- 2 unresolved_issue entries (from commit messages referencing open GitHub issues)
```

---

### 12.2 Example Investigation Report

```markdown
# Investigation Report
**Task ID:** 3fa85f64
**Issue:** #2851 — NullPointerError when parsing empty string in url_encode
**Investigator:** Issue Investigator Agent
**Date:** 2026-10-31T12:30:00Z

## Issue Summary
Users report that calling `url_encode("")` with an empty string raises an AttributeError:
`'NoneType' object has no attribute 'split'`

## Affected Code
- **File:** `src/flask/utils.py`
- **Function:** `url_encode(value, charset='utf-8')`
- **Lines:** 142–158

## Root Cause (Confidence: High)
The function calls `value.split('&')` on line 147 without checking if `value` is None or empty.
The parameter type annotation says `str` but the function does not guard against callers passing an
empty string, which after `strip()` becomes falsy.

The bug was introduced in commit `a3f9b12` (2024-03-15, "refactor: simplify url encoding").
Before that commit, there was an early return for empty input on line 143.
The refactor removed the early return, introducing the regression.

## Repair Specification
- **Target file:** `src/flask/utils.py`
- **Target function:** `url_encode`
- **Action:** Restore the early return guard: `if not value: return {}`
- **Insert after line:** 143 (after parameter type coercion)
- **Constraint:** Do not change the function's public signature or return type

## Ghost Memory Referenced
- Memory entry `arch-001`: "url_encode is called by 8 other modules — do not change its return type"
- Memory entry `fix-003`: "Previous attempt to add try-catch here caused issues with the test suite"
```

---

### 12.3 Example Review Verdict

```markdown
# Review Verdict
**Task ID:** 3fa85f64
**Patch Iteration:** 2
**Reviewer:** Adversarial Reviewer Agent
**Date:** 2026-10-31T13:00:00Z

## Verdict: ACCEPTED ✓

## Analysis

### Does the patch fix the reported issue?
Yes. The early return `if not value: return {}` on line 143 prevents the AttributeError
when an empty string is passed. Tested logic path confirmed.

### Regression Risk Assessment
Low. The early return path was previously present (per Git history). The change is minimal
and does not affect any other code path. The 8 callers of `url_encode` all pass non-empty
strings in normal operation; they will now receive `{}` instead of an exception for empty
input, which is the more useful behavior.

### Security Observations
None. The patch does not introduce any new code execution paths, external calls, or
data handling changes.

### Edge Cases Verified
- `url_encode("")` → `{}` (previously: AttributeError)
- `url_encode("a=1&b=2")` → `{'a': '1', 'b': '2'}` (unchanged)
- `url_encode(None)` → type error (not addressed, but not in scope per specification)

### Alternative Approaches Considered
A try-except block was considered but rejected per Ghost Memory entry `fix-003`.
The early return is the cleaner and historically-correct solution.
```

---

### 12.4 Example Verification Report

```markdown
# Verification Report
**Task ID:** 3fa85f64
**Patch Iteration:** 2
**Test Engineer:** Test Engineer Agent
**Date:** 2026-10-31T13:20:00Z

## Test Environment
- Container image: python:3.12-slim
- Network: none
- CPU: 2 cores | Memory: 2 GB | Timeout: 600s
- Test framework: pytest 8.3.0

## Test Command
`python -m pytest tests/test_utils.py tests/ -v --tb=short`

## Results
| Metric | Value |
|---|---|
| Total tests | 247 |
| Passed | 247 |
| Failed | 0 |
| Errors | 0 |
| Duration | 42.3 seconds |
| Exit code | 0 |

## New Test Coverage
The patch's affected code path (`url_encode` with empty input) is now exercised by:
- `tests/test_utils.py::test_url_encode_empty_string` (newly detectable, was previously hidden by exception)

## Verification Conclusion
All existing tests pass. The patch does not introduce regressions.
The reported issue is resolved: `url_encode("")` now returns `{}` without raising an exception.
```

---

### 12.5 Example GitHub PR Description

```markdown
## SPECTER Maintenance Report

> This pull request was generated by [SPECTER — The Ghost Maintainer](https://github.com/your-org/specter).
> A human reviewed and approved this change before it was submitted.

### Issue Fixed
**#2851 — NullPointerError when parsing empty string in url_encode**

Closes #2851

### Root Cause

The function `url_encode` in `src/flask/utils.py` called `value.split('&')` without
guarding against empty or None input. This regression was introduced in commit `a3f9b12`
(2024-03-15) during a refactor that removed the original early-return guard.

### Change Summary

```diff
--- a/src/flask/utils.py
+++ b/src/flask/utils.py
@@ -142,6 +142,8 @@ def url_encode(value, charset='utf-8'):
     """
+    if not value:
+        return {}
     parts = []
     for key, values in _iter_multi_dict(value):
```

**Files changed:** 1 | **Lines added:** 2 | **Lines removed:** 0

### Review

This patch was independently reviewed by SPECTER's Adversarial Reviewer agent:

- ✅ Fixes the reported issue
- ✅ No regression risk (historically-correct solution)
- ✅ No security concerns
- ✅ All 247 existing tests pass

### Test Results

| Metric | Result |
|---|---|
| Test framework | pytest 8.3.0 |
| Tests run | 247 |
| Passed | 247 ✅ |
| Failed | 0 |
| Test environment | Isolated Docker container, no network access |

---
*Generated by SPECTER v0.1.0 — Task ID: 3fa85f64*
*This PR requires human review and approval before merging.*
```
