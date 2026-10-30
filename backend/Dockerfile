# Multi-stage Dockerfile for SPECTER Rust Axum API Service
FROM rust:1.80-slim AS builder

WORKDIR /usr/src/specter-backend

# Install build dependencies
RUN apt-get update && apt-get install -y pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*

COPY Cargo.toml Cargo.lock ./
COPY migrations ./migrations
COPY src ./src

RUN cargo build --release

FROM debian:bookworm-slim AS runner

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /usr/src/specter-backend/target/release/specter-backend /app/specter-backend

ENV SPECTER_HOST=0.0.0.0
ENV SPECTER_PORT=8080
ENV SPECTER_ENV=production

EXPOSE 8080

CMD ["/app/specter-backend"]
