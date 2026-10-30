# SPECTER Testing Prompts Specification

## 1. Test Discovery & Execution Planning Prompt Template

```markdown
### TASK: Plan Isolated Test Execution
You are the Test Engineer. Discover the testing framework from the repository manifest and construct an isolated container execution plan.

**Repository Configuration Files**:
```
{manifest_files_content}
```

**Proposed Patch**:
```diff
{patch_diff}
```

Instructions:
1. Identify the build tool and test runner (e.g. `pytest`, `cargo test`, `npm test`, `go test`).
2. Specify the base container image required (e.g. `rust:1.80-slim`, `python:3.12-slim`, `node:20-alpine`).
3. Formulate the exact execution commands:
   - Target existing tests related to the modified files.
   - Run the complete regression test suite.
4. Enforce security constraints: network disabled (`--network none`), memory limit (`--memory 2g`), timeout (`--timeout 300`).

Output valid JSON matching the Test Plan schema.
```

---

## 2. Test Verification Report Generation Template

```markdown
### TASK: Analyze Test Container Results
Analyze the raw container execution logs and generate the official Verification Report.

**Exit Code**: {container_exit_code}
**Execution Duration**: {duration_seconds}s

**Container stdout/stderr**:
```
{container_output}
```

Instructions:
1. Determine whether all relevant tests passed.
2. Highlight any newly introduced failures vs pre-existing broken tests.
3. Produce a structured Verification Report conforming to `agent/schemas/agent-output.schema.json`.
```
