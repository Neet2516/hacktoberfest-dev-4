use std::env;

#[derive(Debug, Clone)]
pub struct AppConfig {
    pub host: String,
    pub port: u16,
    pub environment: String,
}

impl AppConfig {
    pub fn from_env() -> Self {
        let host = env::var("SPECTER_HOST").unwrap_or_else(|_| "127.0.0.1".to_string());
        let port = env::var("SPECTER_PORT")
            .ok()
            .and_then(|p| p.parse().ok())
            .unwrap_or(8080);
        let environment = env::var("SPECTER_ENV").unwrap_or_else(|_| "development".to_string());

        Self {
            host,
            port,
            environment,
        }
    }

    pub fn socket_addr(&self) -> String {
        format!("{}:{}", self.host, self.port)
    }
}
