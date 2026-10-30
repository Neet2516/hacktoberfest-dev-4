# SPECTER Sequential Handoff Protocol

## 1. Pipeline Sequence
SPECTER's core maintenance pipeline executes sequentially across specialized agents:

1. **Repository Archaeologist** $\rightarrow$ Repository Context Report
2. **Issue Investigator** $\rightarrow$ Issue Reproduction & Repair Specification
3. **Ghost Repairer** $\rightarrow$ Candidate Git Patch
4. **Adversarial Reviewer** $\rightarrow$ Adversarial Review Verdict
5. **Test Engineer** $\rightarrow$ Containerized Verification Report
6. **Resurrection Coordinator** $\rightarrow$ Human Approval Proposal

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
