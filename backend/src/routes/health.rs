use axum::{extract::State, http::StatusCode, response::IntoResponse, Json};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

use crate::db::DatabaseService;

#[derive(Clone, Default)]
pub struct AppState {
    pub db: Option<Arc<DatabaseService>>,
}

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

pub async fn readiness_check(State(state): State<AppState>) -> impl IntoResponse {
    let mut checks = vec![HealthCheckItem {
        name: "api_router".to_string(),
        status: "operational".to_string(),
    }];

    let db_status = if let Some(ref db) = state.db {
        match db.ping().await {
            Ok(true) => "operational",
            _ => "unreachable",
        }
    } else {
        "unconfigured"
    };

    checks.push(HealthCheckItem {
        name: "database".to_string(),
        status: db_status.to_string(),
    });

    let is_ready = db_status != "unreachable";

    let payload = ReadinessStatus {
        ready: is_ready,
        checks,
    };

    let status_code = if is_ready {
        StatusCode::OK
    } else {
        StatusCode::SERVICE_UNAVAILABLE
    };

    (status_code, Json(payload))
}

pub async fn version_info() -> impl IntoResponse {
    let payload = VersionInfo {
        version: env!("CARGO_PKG_VERSION").to_string(),
        commit: "dev".to_string(),
        challenge: "Hacktoberfest 2026 — Ghost in the Machine".to_string(),
    };
    (StatusCode::OK, Json(payload))
}
