# SPECTER — REST API Reference

All requests to the SPECTER Backend API use JSON envelopes and standard HTTP status codes.

## Endpoints

### 1. Health & Readiness
- `GET /health` -> Returns `{"status": "ok", "service": "specter-backend"}`
- `GET /ready` -> Returns `{"status": "ready", "database": "connected"}`
- `GET /api/v1/version` -> Returns service semver and git commit hash.

### 2. Repository Ingestion
- `POST /api/v1/repositories/ingest`
  - Body: `{"url": "https://github.com/org/abandoned-repo"}`
  - Response: `{"id": "...", "status": "ingested", "owner": "...", "name": "..."}`
  - Validation: Enforces HTTPS, public github.com origin, and strict SSRF loopback protections.

### 3. Maintenance Proposals & Human Approval Gate
- `GET /api/v1/proposals/:proposal_id` -> Returns proposal diff, verification summary, and approval state.
- `POST /api/v1/proposals/:proposal_id/approve`
  - Body: `{"reviewer": "maintainer_handle"}`
  - Action: Signs cryptographic proposal hash and permits remote PR generation.
- `POST /api/v1/proposals/:proposal_id/reject`
  - Body: `{"reviewer": "maintainer_handle", "feedback": "Detailed reason"}`
  - Action: Marks proposal rejected and triggers negative test case recording.

