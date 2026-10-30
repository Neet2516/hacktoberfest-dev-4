FROM python:3.12-slim

WORKDIR /app

# Install security certificates and Git
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY specter_runtime ./specter_runtime
COPY tests ./tests

# Run self-test verification during build
RUN python -m unittest discover -s tests

ENV PYTHONUNBUFFERED=1
ENV TEMPORAL_HOST=temporal:7233
ENV OLLAMA_HOST=http://ollama:11434

CMD ["python", "-m", "specter_runtime"]
