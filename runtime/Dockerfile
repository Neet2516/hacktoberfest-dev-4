# Multi-stage Dockerfile for SPECTER Python Autonomous Agent Runtime
FROM python:3.12-slim AS builder

WORKDIR /app

# Install security certificates, Git, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY specter_runtime ./specter_runtime
COPY tests ./tests

ENV PYTHONPATH=/app
ENV SPECTER_ENV=test

# Run self-test verification during build
RUN python -m unittest discover -s tests

FROM python:3.12-slim AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/specter_runtime ./specter_runtime

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV TEMPORAL_HOST=temporal:7233
ENV OLLAMA_HOST=http://ollama:11434

CMD ["python", "-m", "specter_runtime"]
