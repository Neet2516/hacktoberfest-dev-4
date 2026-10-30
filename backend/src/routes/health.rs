use axum::{http::StatusCode, response::IntoResponse, Json};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct HealthStatus {
    pub status: String,
    pub service: String,
    pub version: String,
}

#[derive(Serialize, Deserialize)]
pub struct ReadinessStatus {
    pub ready: bool,
    pub checks: Vec<HealthCheckItem>,
}

#[derive(Serialize, Deserialize)]
pub struct HealthCheckItem {
    pub name: String,
    pub status: String,
}

#[derive(Serialize, Deserialize)]
pub struct VersionInfo {
    pub version: String,
    pub commit: String,
    pub challenge: String,
}

pub async fn health_check() -> impl IntoResponse {
    let payload = HealthStatus {
        status: "ok".to_string(),
        service: "specter-backend".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
    };
    (StatusCode::OK, Json(payload))
}

pub async fn readiness_check() -> impl IntoResponse {
    let payload = ReadinessStatus {
        ready: true,
        checks: vec![
            HealthCheckItem {
                name: "api_router".to_string(),
                status: "operational".to_string(),
            },
        ],
    };
    (StatusCode::OK, Json(payload))
}

pub async fn version_info() -> impl IntoResponse {
    let payload = VersionInfo {
        version: env!("CARGO_PKG_VERSION").to_string(),
        commit: "dev".to_string(),
        challenge: "Hacktoberfest 2026 — Ghost in the Machine".to_string(),
    };
    (StatusCode::OK, Json(payload))
}
