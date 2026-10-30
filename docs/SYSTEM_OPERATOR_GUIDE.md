# SPECTER — System Operator Guide

## 1. Operating Procedures
- **Monitoring Agents**: Query `/api/v1/metrics` or inspect OpenTelemetry traces in Jaeger/Prometheus.
- **Managing Database**: Connect via `psql` to query `tasks`, `repositories`, and `ghost_memory` tables.
- **Resource Constraints**: Ensure Docker container daemon enforces cgroup quotas (default `--memory 2g`, `--cpus 2.0`).

## 2. Security Containment Audit
- Verify that disposable test containers always execute with `--network none`.
- Check that host workspace directories are mounted strictly `:ro` (read-only).
- Ensure `GITHUB_TOKEN` is never stored in prompt template files or agent message payloads.

