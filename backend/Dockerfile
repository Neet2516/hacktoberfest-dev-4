FROM rust:1.80-slim as builder

WORKDIR /usr/src/specter-backend
COPY Cargo.toml Cargo.lock ./
COPY src ./src

RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /usr/src/specter-backend/target/release/backend /app/specter-backend

ENV SPECTER_HOST=0.0.0.0
ENV SPECTER_PORT=8080
ENV SPECTER_ENV=production

EXPOSE 8080

CMD ["/app/specter-backend"]

