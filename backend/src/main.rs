use specter_backend::{create_router_with_state, AppConfig, AppState, DatabaseService};
use std::sync::Arc;
use tokio::net::TcpListener;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "specter_backend=debug,tower_http=debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    let config = AppConfig::from_env();
    let addr = config.socket_addr();

    tracing::info!(
        service = "specter-backend",
        version = env!("CARGO_PKG_VERSION"),
        addr = %addr,
        environment = %config.environment,
        "Starting SPECTER backend service"
    );

    // Optional connection to database on startup
    let db = match DatabaseService::connect(&config.database_url, config.max_db_connections, 5).await {
        Ok(service) => {
            tracing::info!("Connected to PostgreSQL database");
            Some(Arc::new(service))
        }
        Err(err) => {
            tracing::warn!(error = %err, "Proceeding without active database connection");
            None
        }
    };

    let app_state = AppState { db };
    let app = create_router_with_state(app_state);
    let listener = TcpListener::bind(&addr).await?;
    
    tracing::info!("Listening on http://{}", addr);
    axum::serve(listener, app).await?;

    Ok(())
}
