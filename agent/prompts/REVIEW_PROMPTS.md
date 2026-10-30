# SPECTER Review Prompts Specification

## 1. Adversarial Audit Prompt Template

```markdown
### TASK: Conduct Adversarial Code Review
You are the Adversarial Reviewer. Critically audit the candidate patch below against the repair specification and repository baseline.

**Repair Specification**:
```json
{repair_specification_json}
```

**Proposed Git Patch**:
```diff
{patch_diff}
```

**Surrounding Context**:
```
{surrounding_code_context}
```

AUDIT CHECKLIST:
1. **Correctness**: Does the patch genuinely solve the root cause, or is it a superficial band-aid?
2. **Regressions**: Can this change break existing callers or introduce subtle off-by-one / null pointer / race conditions?
3. **Over-refactoring**: Did the author change formatting, variable names, or logic outside the necessary scope?
4. **Security**: Does this change introduce injection, memory safety violations, unchecked user input, or insecure dependencies?
5. **Preservation**: Were all explicit preservation constraints respected?

Output your report as valid JSON conforming to `agent/schemas/review-report.schema.json`.
```

---

## 2. Review Report Output Example

```json
{
  "review_id": "rev_01HJ8Z9X",
  "task_id": "SPECTER-074",
  "reviewer_agent": "adversarial_reviewer",
  "verdict": "REQUEST_CHANGES",
  "regression_risk": "MEDIUM",
  "security_risk": "NONE",
  "findings": [
    {
      "finding_id": "F-01",
      "severity": "ERROR",
      "category": "REGRESSION",
      "description": "Returning LexerError::UnexpectedEof breaks compatibility with caller in parse_expression which expects Option<Token>.",
      "file_path": "src/parser/lexer.rs",
      "line_number": 124,
      "suggested_remediation": "Wrap error in existing LexResult enum variant"
    }
  ],
  "corrections_required": [
    "Align return type with LexResult::Err(LexerError::UnexpectedEof)"
  ],
  "approved": false,
  "timestamp": "2026-10-31T00:25:00Z"
}
```
