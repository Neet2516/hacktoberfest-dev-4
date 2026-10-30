# SPECTER Task Template

> Copy this file to `tasks/backlog/SPECTER-NNN.md` and fill in every field.  
> Do **not** leave any field blank. Use `None` or `N/A` only when genuinely not applicable.

---

## Task ID
`SPECTER-NNN`

---

## Task Title
<!-- One-line imperative sentence describing what is being built or done -->
<!-- Example: "Implement PostgreSQL connection pool in Rust" -->

---

## Epic
<!-- EPIC NN — Epic Name (e.g., EPIC 02 — Backend Infrastructure) -->

---

## Priority
<!-- One of: P0 / P1 / P2 / P3 -->
<!-- P0 = Critical foundation | P1 = MVP required | P2 = Enhancement | P3 = Post-MVP -->

---

## Objective
<!-- 2–4 sentences describing WHY this task exists, what problem it solves, and its role
     in the broader SPECTER system. Be specific. -->

---

## PRD Requirement Reference
<!-- One or more of FR-01 through FR-14. List all that apply.
     Example: FR-02 (clone repo), FR-09 (isolated test execution) -->

---

## Technical Specification
<!-- Detailed technical description of WHAT is being built:
     - Language / framework / library choices with versions
     - Data models or schemas (show field names and types)
     - API contracts (endpoints, request/response shapes)
     - Algorithms or key logic description
     - Integration points with other components
     Use code blocks where helpful. -->

---

## Dependencies
<!-- Comma-separated list of SPECTER task IDs that must be COMPLETED before this task
     can start. Example: SPECTER-001, SPECTER-005
     Use "None" if this is a root task. -->

---

## Responsible Agent / Human Owner
<!-- One of:
     - Repository Archaeologist
     - Issue Investigator
     - Ghost Repairer
     - Adversarial Reviewer
     - Test Engineer
     - Resurrection Coordinator
     - Human/DevOps
     - Frontend Developer
     - Security Engineer
-->

---

## Input Requirements
<!-- What must exist / be available for this task to begin?
     - Files, services, configurations, credentials, prior task outputs
     - Be specific: "PostgreSQL running on localhost:5432 with SPECTER_DB database created" -->

---

## Expected Output
<!-- What artifacts does this task produce?
     - File paths (relative to project root)
     - API endpoints
     - Database schema changes
     - Docker images or configurations
     Be specific and verifiable. -->

---

## Implementation Steps
<!-- Numbered, ordered list of concrete steps. Each step should be actionable by an agent
     or developer without further clarification. -->

1. Step one
2. Step two
3. Step three
<!-- ... -->

---

## Files Affected
<!-- List of files created, modified, or deleted by this task.
     Use relative paths from project root.
     Example:
     - Created: `backend/src/db/pool.rs`
     - Modified: `backend/Cargo.toml`
     - Deleted: N/A -->

---

## Security Considerations
<!-- Describe any security risks introduced by this task and how they are mitigated.
     Required for ALL tasks that:
     - Accept external input (URLs, user data, file uploads)
     - Execute code or commands
     - Handle credentials or tokens
     - Interact with the filesystem or network
     If none apply, write "No external input, code execution, or credential handling in this task." -->

---

## Testing Requirements
<!-- How will correctness be verified?
     - Unit test file locations
     - Integration test scenarios
     - Test data / fixtures needed
     - Expected pass/fail outcomes -->

---

## Acceptance Criteria
<!-- Checkable list. Each item must be independently verifiable.
     Mark as [ ] (unchecked) initially. -->

- [ ] Criterion one
- [ ] Criterion two
- [ ] Criterion three
<!-- ... -->

---

## Definition of Done
<!-- The exhaustive checklist that a reviewer uses to confirm this task is truly complete.
     Unlike Acceptance Criteria (which are functional), DoD covers process and quality. -->

- [ ] All acceptance criteria are checked
- [ ] Code is committed and pushed to the feature branch
- [ ] Unit tests written and passing (≥80% coverage for new code)
- [ ] Integration tests passing in CI
- [ ] No new linter warnings or compiler errors introduced
- [ ] Security considerations documented and addressed
- [ ] Files Affected list matches what was actually changed
- [ ] Task file moved to `tasks/completed/`
- [ ] Evidence of Completion section filled in
- [ ] TASK_INDEX.md updated to reflect COMPLETED status

---

## Current Status
<!-- Format: STATUS — YYYY-MM-DD HH:MM UTC — brief note
     Example: IN-PROGRESS — 2025-11-01 14:00 UTC — Repository Archaeologist working on parser integration -->

BACKLOG — <!-- date --> — Not yet scheduled

---

## Blockers
<!-- Describe any current blockers preventing progress.
     Format: [BLOCKER TYPE] Description — Who must resolve — Target resolution date
     Types: DEPENDENCY | DECISION | EXTERNAL | RESOURCE
     Use "None" if no blockers. -->

None

---

## Evidence of Completion
<!-- Filled in when task moves to COMPLETED.
     Include:
     - Git commit SHA or PR link
     - CI run link (green)
     - Test report summary
     - Any deployed artifact URLs
     Leave blank (write "Pending") until task is done. -->

Pending
