# SPECTER Error Code Registry

| Error Code | Category | HTTP Status | Description | Remediation |
|---|---|---|---|---|
| `ERR_INGEST_INVALID_URL` | Ingestion | 400 | Repository URL failed format validation or contains invalid domain | Verify URL points to public github.com repository |
| `ERR_INGEST_SSRF_DETECTED` | Security | 400 | Repository URL resolves to private, loopback, or cloud metadata IP | Disallow internal IP addresses and non-standard schemes |
| `ERR_INGEST_CLONE_FAILED` | Ingestion | 502 | Shallow clone of repository failed or timed out | Check network connectivity and repository availability |
| `ERR_FS_ISOLATION_BREACH` | Security | 403 | Attempted path traversal outside `workspace://` root | Enforce strict virtual path mapper canonicalization |
| `ERR_AGENT_TIMEOUT` | Agent Runtime | 504 | Agent execution exceeded default timeout quota | Adjust complexity budget or break task into smaller sub-tasks |
| `ERR_TOOL_ACCESS_DENIED` | Agent Runtime | 403 | Agent role attempted invocation of unassigned tool contract | Enforce least-privilege role matrix |
| `ERR_MSG_SCHEMA_INVALID` | Communication | 422 | Inter-agent message failed validation against schema | Ensure all required message envelope fields are present |
| `ERR_REVIEW_REJECTED` | Quality Gate | 409 | Adversarial review detected security blocker or over-refactoring | Loop back to Ghost Repairer with rejection findings |
| `ERR_TEST_EXECUTION_FAILED` | Testing | 500 | Isolated disposable container failed test execution | Inspect test runner output and patch logic |
| `ERR_GATE_UNAUTHORIZED` | Human Gate | 401 | Remote branch mutation attempted without signed human approval | Submit proposal to maintainer dashboard for explicit signoff |
| `ERR_SECRET_EXPOSURE_RISK` | Security | 400 | Sensitive token or secret detected in diff or prompt | Scrub credentials immediately and reject diff |
