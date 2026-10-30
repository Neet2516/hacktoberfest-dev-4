# SPECTER Investigation Prompts Specification

## 1. Repository Archaeology Prompt Template

```markdown
### TASK: Analyze Repository Architecture & History
**Repository Workspace**: {workspace_path}
**Baseline Commit**: {commit_sha}

Analyze the codebase and generate a comprehensive Repository Context Report.
Cover the following sections in valid JSON:
1. `primary_languages`: Array of detected languages with percentages.
2. `architecture_pattern`: Architectural style (e.g., modular monolith, clean architecture, CLI tool).
3. `build_system`: Build tool, package manager, and configuration entrypoints.
4. `test_frameworks`: Detected testing tools and conventions.
5. `historical_insights`: Key architectural decisions reconstructed from recent commit logs.
6. `unresolved_smells`: Inactive modules or known broken dependencies.

Input Data:
```
{repo_summary_data}
```
```

---

## 2. Issue Analysis & Root Cause Deduction Prompt Template

```markdown
### TASK: Investigate GitHub Issue
**Issue ID**: #{issue_number}
**Title**: {issue_title}
**Reporter**: {issue_author}

**Issue Body**:
```
{issue_body}
```

**Repository Context Summary**:
```
{repo_context_summary}
```

Instructions:
1. Identify the specific symptoms reported.
2. Cross-reference repository symbols to locate affected files and functions.
3. Trace the execution path that triggers the failure.
4. Identify the root cause (e.g., off-by-one, unhandled error, type mismatch, race condition).
5. Generate a formal Repair Specification in JSON matching the SPECTER schema.
```

---

## 3. Repair Specification Output Structure

```json
{
  "specification_id": "spec_issue_42",
  "issue_id": 42,
  "affected_files": [
    {
      "path": "src/parser/lexer.rs",
      "symbols": ["tokenize_string", "consume_escape_sequence"],
      "lines": [112, 128]
    }
  ],
  "root_cause_analysis": "Underflow occurs when string ends abruptly on an unescaped backslash.",
  "required_behavior": "Return LexerError::UnexpectedEof instead of panicking on slice index.",
  "preservation_constraints": [
    "Do not alter token enum variants",
    "Preserve Lexer public constructor"
  ],
  "verification_strategy": "Run cargo test parser::tests::test_unterminated_escape"
}
```
