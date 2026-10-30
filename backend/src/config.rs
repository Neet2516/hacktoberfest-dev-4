use std::env;

#[derive(Debug, Clone)]
pub struct AppConfig {
    pub host: String,
    pub port: u16,
    pub environment: String,
    pub database_url: String,
    pub max_db_connections: u32,
}

impl AppConfig {
    pub fn from_env() -> Self {
        let host = env::var("SPECTER_HOST").unwrap_or_else(|_| "127.0.0.1".to_string());
        let port = env::var("SPECTER_PORT")
            .ok()
            .and_then(|p| p.parse().ok())
            .unwrap_or(8080);
        let environment = env::var("SPECTER_ENV").unwrap_or_else(|_| "development".to_string());
        let database_url = env::var("DATABASE_URL").unwrap_or_else(|_| {
            "postgresql://specter_admin:specter_secure_dev_pass_2026@localhost:5432/specter"
                .to_string()
        });
        let max_db_connections = env::var("MAX_DB_CONNECTIONS")
            .ok()
            .and_then(|c| c.parse().ok())
            .unwrap_or(20);

        Self {
            host,
            port,
            environment,
            database_url,
            max_db_connections,
        }
    }

    pub fn socket_addr(&self) -> String {
        format!("{}:{}", self.host, self.port)
    }
}
