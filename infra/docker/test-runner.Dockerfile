# SPECTER Disposable Test Runner Sandbox
# PRD Section 11 & EPIC 12: Executed exclusively with --network none and strict resource quotas

FROM debian:bookworm-slim

# Install core build toolchains and package managers
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    build-essential \
    curl \
    git \
    python3 \
    python3-pip \
    nodejs \
    npm \
    cargo \
    rustc \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged sandbox user
RUN useradd -u 10001 -m -s /bin/bash specter_sandbox

USER specter_sandbox
WORKDIR /workspace

# Default command displays isolation message
CMD ["echo", "SPECTER Isolated Test Sandbox Ready. Networking disabled."]

