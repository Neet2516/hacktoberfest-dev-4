pub mod health;

use axum::{routing::get, Router};
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
        .with_state(state)
        .layer(cors)
        .layer(TraceLayer::new_for_http())
}
