use sqlx::postgres::{PgPool, PgPoolOptions};
use std::time::Duration;

#[derive(Clone, Debug)]
pub struct DatabaseService {
    pool: PgPool,
}

impl DatabaseService {
    pub async fn connect(
        database_url: &str,
        max_connections: u32,
        acquire_timeout_secs: u64,
    ) -> Result<Self, sqlx::Error> {
        tracing::info!(
            max_connections = max_connections,
            acquire_timeout_secs = acquire_timeout_secs,
            "Initializing PostgreSQL connection pool"
        );

        let pool = PgPoolOptions::new()
            .max_connections(max_connections)
            .acquire_timeout(Duration::from_secs(acquire_timeout_secs))
            .idle_timeout(Duration::from_secs(300))
            .connect(database_url)
            .await?;

        tracing::info!("PostgreSQL connection pool established successfully");
        Ok(Self { pool })
    }

    pub fn pool(&self) -> &PgPool {
        &self.pool
    }

    pub async fn ping(&self) -> Result<bool, sqlx::Error> {
        sqlx::query("SELECT 1")
            .execute(&self.pool)
            .await
            .map(|_| true)
    }
}
