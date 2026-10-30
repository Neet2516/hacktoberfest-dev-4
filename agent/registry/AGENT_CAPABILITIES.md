# SPECTER Agent Capabilities Matrix

**Version:** 1.0.0
**Reference:** TOOL_CONTRACTS.md, SAFETY_POLICY.md

---

> This document defines what each SPECTER agent CAN and CANNOT do. It supplements per-agent role documents with a cross-cutting capability view.

---

## 1. Capability Matrix Summary

| Capability | Coordinator | Archaeologist | Investigator | Ghost Repairer | Adv. Reviewer | Test Engineer |
|-----------|:-----------:|:-------------:|:------------:|:--------------:|:-------------:|:-------------:|
| **Read GitHub issues** | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Create GitHub PR** | ✅ (post-approval) | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Push git branch** | ✅ (post-approval) | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Clone repository** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Read repository files** | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Write repository files** | ❌ | ❌ | ❌ | ✅ (workspace only) | ❌ | ❌ |
| **Parse code (Tree-sitter)** | ❌ | ✅ | ❌ | ✅ (validation) | ✅ | ❌ |
| **Generate embeddings** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Semantic search (pgvector)** | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **LLM inference (Ollama)** | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Run Docker containers** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Assign tasks to agents** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Transition task state** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Request human approval** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Write investigation report** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Write patch proposal** | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Write review report** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Write test results** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Write repo analysis** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Read audit log** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Write audit log** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Read own task state** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Read other task state** | ✅ (own tasks only) | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Cancel other agents** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Merge pull requests** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Execute code on host** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Access credentials** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Legend:** ✅ = Permitted (within constraints) | ❌ = Prohibited

---

## 2. Detailed Capabilities by Agent

### 2.1 Resurrection Coordinator

**CAN:**
- Create and manage Temporal workflow instances for tasks
- Send DELEGATE messages to specialist agents
- Receive and validate RESULT messages from specialist agents
- Transition task status (BACKLOG → READY → IN-PROGRESS → REVIEW → AWAITING_APPROVAL → COMPLETED)
- Enforce quality gates at each state transition
- Request human approval via UI notification
- Push a branch to GitHub (after human approval AG-01)
- Create a pull request on GitHub (after human approval AG-02)
- Cancel running agent activities on failure
- Write to `tasks`, `task_events`, `task_checkpoints`, `approvals`, `audit_log` tables
- Read from all task-related tables (for oversight)
- Retry failed phases up to the configured maximum

**CANNOT:**
- Merge pull requests
- Perform direct code analysis or patch generation
- Access repository files directly
- Pass credentials to any agent
- Skip or defer quality gates
- Modify the `audit_log` table (only INSERT)
- Assign tasks to agents outside defined workflow sequence
- Make decisions about patch correctness (delegates to Reviewer)

---

### 2.2 Repository Archaeologist

**CAN:**
- Read any file within the cloned repository workspace
- Enumerate directory structures recursively
- Parse source files with Tree-sitter (all supported languages)
- Extract: imports, exports, function signatures, class definitions, call graphs
- Generate file-level semantic embeddings via Ollama
- Store embeddings to pgvector
- Build and store repository map (file_map table)
- Read repository metadata from GitHub (language stats, topics, size)
- Read git log, git diff, git blame (read-only)
- Report partial results if some files fail to parse (with warnings)

**CANNOT:**
- Write or modify any file in the workspace
- Create git branches or commits
- Execute any code from the repository
- Access GitHub issue content directly (Investigator's role)
- Access the `investigation_reports`, `patches`, `review_reports`, or `test_results` tables
- Infer root cause or suggest fixes (analysis only)

---

### 2.3 Issue Investigator

**CAN:**
- Retrieve full issue thread (body, comments, timeline) from GitHub
- Perform semantic similarity search on repo map embeddings (pgvector)
- Search for similar historical issues on GitHub
- Trace code paths from issue symptoms to likely root causes
- Read repository files (in workspace) to verify hypotheses
- Access git blame and log for affected files
- Generate root cause hypotheses using Ollama/Gemma
- Produce investigation report with: root cause, affected files, confidence score, evidence
- Read from: `repo_analysis`, `file_map`, `embeddings` tables
- Write to: `investigation_reports` table

**CANNOT:**
- Generate or propose code patches
- Create git branches
- Modify repository files
- Access `patches`, `review_reports`, or `test_results` tables
- Set task status (Coordinator's role)
- Make final root cause determinations with confidence < 0.60 (must escalate)

---

### 2.4 Ghost Repairer

**CAN:**
- Read investigation report and repository map from database
- Read repository files in workspace
- Generate patch proposals using Ollama/Gemma (following REPAIR_PROMPTS.md)
- Write patch files to workspace (`/workspaces/<taskId>/patches/`)
- Create a git branch in workspace (does NOT push)
- Apply patches to workspace clone using `git apply`
- Validate patched code syntax with Tree-sitter
- Generate a git diff of proposed changes
- Write to `patches` table (patch record, diff content)
- Read from `investigation_reports`, `repo_analysis`, `file_map` tables

**CANNOT:**
- Push branches to any remote
- Access GitHub API
- Execute tests or build the code
- Modify files outside the scope defined in the investigation report (+ max 2 adjacent files)
- Generate patches larger than 500 lines changed
- Delete existing test files
- Access `review_reports` or `test_results` tables

---

### 2.5 Adversarial Reviewer

**CAN:**
- Read patch diff from workspace and database
- Read investigation report and repository map for context
- Analyze patch for correctness, completeness, and regression risk
- Search GitHub for similar past fixes and their outcomes
- Use Ollama/Gemma to generate adversarial review analysis
- Identify security implications of the patch
- Produce a review report with: verdict, findings, risk assessments, corrections
- Write to `review_reports` table
- Read from `patches`, `investigation_reports`, `repo_analysis` tables

**CANNOT:**
- Modify the patch directly
- Generate alternative patches (must return verdict to Coordinator)
- Approve its own generated content (cannot be both Repairer and Reviewer)
- Access test results (test phase has not occurred yet)
- Set task status
- Approve or create PRs

---

### 2.6 Test Engineer

**CAN:**
- Read patch proposal from database
- Run Docker containers using pre-built SPECTER test runner images
- Mount repository (read-only) into containers
- Execute test suites inside containers
- Read container stdout/stderr logs
- Categorize test results (PASS/FAIL/ERROR/SKIP per test)
- Determine coverage delta (if tooling present)
- Classify test verdict (ALL_PASS, PARTIAL_PASS, ALL_FAIL, ERROR)
- Write to `test_results`, `container_logs` tables
- Kill containers exceeding timeout
- Remove containers after completion

**CANNOT:**
- Execute code on the host OS (all execution is inside containers)
- Pull Docker images from external registries at runtime
- Run containers with elevated privileges
- Access GitHub API
- Access investigation reports or review reports directly (receives task context from Coordinator)
- Modify patch files
- Interpret test failures as root causes (reports facts; Coordinator routes)
- Install packages inside containers

---

## 3. Cross-Cutting Capabilities

### 3.1 All Agents CAN:
- Send messages to the Coordinator (RESULT, STATUS_UPDATE, ESCALATION)
- Write to the audit log (INSERT only)
- Read their own task state from Temporal
- Send heartbeats to Temporal
- Fail their own Temporal activity (triggering retry logic)
- Report security violations to the Coordinator

### 3.2 No Agent CAN:
- Merge pull requests (human-only)
- Execute repository code on the host (Docker sandbox only)
- Access credentials or tokens
- Modify other agents' outputs once written
- Override quality gates
- Communicate peer-to-peer (all messages go through Coordinator)
- Modify the SPECTER system configuration
- Delete audit log records
