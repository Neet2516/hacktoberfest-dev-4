pub mod health;
pub mod ingestion;
pub mod vault;

use axum::{
    routing::{get, post},
    Router,
};
use tower_http::cors::{Any, CorsLayer};
use tower_http::trace::TraceLayer;

pub use health::AppState;

pub fn create_router() -> Router {
    create_router_with_state(AppState::default())
}

pub fn create_router_with_state(state: AppState) -> Router {
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    Router::new()
        .route("/health", get(health::health_check))
        .route("/ready", get(health::readiness_check))
        .route("/api/v1/version", get(health::version_info))
        .route("/api/v1/repos/validate", post(ingestion::validate_repository_url))
        .route("/api/v1/vault/github-token", post(vault::store_github_token))
        .route("/api/v1/vault/status", get(vault::get_vault_status))
        .route("/api/v1/vault/clear", post(vault::clear_vault_token))
        .with_state(state)
        .layer(cors)
        .layer(TraceLayer::new_for_http())
}
