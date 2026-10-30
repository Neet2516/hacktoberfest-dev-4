use specter_backend::{create_router, AppConfig};
use tokio::net::TcpListener;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize structured tracing
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

    let app = create_router();
    let listener = TcpListener::bind(&addr).await?;
    
    tracing::info!("Listening on http://{}", addr);
    axum::serve(listener, app).await?;

    Ok(())
}
