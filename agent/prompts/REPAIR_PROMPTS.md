# SPECTER Repair Prompts Specification

## 1. Minimal Patch Generation Prompt Template

```markdown
### TASK: Generate Minimal Unified Git Patch
You are the Ghost Repairer. Implement a bugfix adhering to the following Repair Specification.

**Repair Specification**:
```json
{repair_specification_json}
```

**Target Source Files (Current Content)**:
```{language}
{target_files_content}
```

STRICT RULES:
1. Output ONLY a unified git diff starting with `diff --git a/... b/...`.
2. Touch ONLY lines strictly necessary to resolve the root cause.
3. Do NOT reformat unaffected code, update comments outside the modified block, or change import ordering.
4. Adhere to all preservation constraints specified in the repair spec.
5. Ensure the patch applies cleanly with `git apply --check`.

Diff output:
```

## 2. Patch Revision After Rejection Prompt Template

```markdown
### TASK: Revise Patch Based on Review & Test Failures
Your previous patch was rejected by the Adversarial Reviewer or failed in test verification.

**Original Repair Specification**:
```json
{repair_specification_json}
```

**Rejected Patch**:
```diff
{rejected_patch_diff}
```

**Reviewer Findings & Required Corrections**:
```json
{reviewer_findings_json}
```

**Test Execution Error Log**:
```
{test_failure_log}
```

Instructions:
1. Address every finding raised by the reviewer.
2. Resolve the test failure without violating preservation constraints.
3. Maintain minimal diff discipline.
4. Output the complete revised unified git diff.
```
