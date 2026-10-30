# SPECTER — Deployment Runbook

## 1. Prerequisites
- Docker Engine >= 24.0.0 & Docker Compose >= 2.20.0
- NVIDIA Container Toolkit (optional, for local GPU Ollama inference)
- Minimum 8 GB RAM, 4 CPU cores, 20 GB free disk space

## 2. Production Deployment Steps
1. Clone the production repository:
   ```bash
   git clone https://github.com/Neet2516/hacktoberfest-dev-4.git specter
   cd specter
   ```
2. Configure environment credentials:
   ```bash
   cp .env.example .env
   # Edit .env with production passwords and GitHub Personal Access Token
   ```
3. Launch services:
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```
4. Verify service health:
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:8080/ready
   ```

## 3. Disaster Recovery & Rollback
- Database backups: `docker exec -t specter-postgres-prod pg_dump -U specter_admin specter > backup.sql`
- Rollback: Re-tag previous release image and restart container mesh.

