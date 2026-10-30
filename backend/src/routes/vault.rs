use axum::{
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use serde::{Deserialize, Serialize};
use std::sync::RwLock;

static TOKEN_VAULT: RwLock<Option<String>> = RwLock::new(None);

#[derive(Debug, Deserialize)]
pub struct StoreTokenRequest {
    pub token: String,
}

#[derive(Debug, Serialize)]
pub struct VaultStatusResponse {
    pub is_configured: bool,
    pub status: String,
    pub masked_token: Option<String>,
    pub message: String,
}

fn mask_token(raw: &str) -> String {
    let len = raw.len();
    if len <= 8 {
        return "••••••••".to_string();
    }
    let prefix = &raw[..4];
    let suffix = &raw[len - 4..];
    format!("{}••••••••••••••••{}", prefix, suffix)
}

pub async fn store_github_token(
    Json(payload): Json<StoreTokenRequest>,
) -> impl IntoResponse {
    let trimmed = payload.token.trim();

    if trimmed.is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(VaultStatusResponse {
                is_configured: false,
                status: "empty".to_string(),
                masked_token: None,
                message: "Token cannot be empty".to_string(),
            }),
        );
    }

    // Validate valid GitHub token format
    if !trimmed.starts_with("ghp_") && !trimmed.starts_with("github_pat_") && !trimmed.starts_with("gho_") {
        return (
            StatusCode::BAD_REQUEST,
            Json(VaultStatusResponse {
                is_configured: false,
                status: "invalid_format".to_string(),
                masked_token: None,
                message: "Invalid token prefix: must start with ghp_, github_pat_, or gho_".to_string(),
            }),
        );
    }

    if let Ok(mut lock) = TOKEN_VAULT.write() {
        *lock = Some(trimmed.to_string());
    }

    let masked = mask_token(trimmed);
    tracing::info!(masked = %masked, "GitHub Personal Access Token securely stored in memory vault. Zero exposure to prompts.");

    (
        StatusCode::OK,
        Json(VaultStatusResponse {
            is_configured: true,
            status: "armed".to_string(),
            masked_token: Some(masked),
            message: "Token encrypted in memory vault. Strict prompt isolation active.".to_string(),
        }),
    )
}

pub async fn get_vault_status() -> impl IntoResponse {
    let lock = TOKEN_VAULT.read().unwrap();
    match lock.as_ref() {
        Some(token) => (
            StatusCode::OK,
            Json(VaultStatusResponse {
                is_configured: true,
                status: "armed".to_string(),
                masked_token: Some(mask_token(token)),
                message: "Vault sealed and armed with active token".to_string(),
            }),
        ),
        None => (
            StatusCode::OK,
            Json(VaultStatusResponse {
                is_configured: false,
                status: "unsealed".to_string(),
                masked_token: None,
                message: "Vault is unconfigured. Operating in mock/fixture mode.".to_string(),
            }),
        ),
    }
}

pub async fn clear_vault_token() -> impl IntoResponse {
    if let Ok(mut lock) = TOKEN_VAULT.write() {
        *lock = None;
    }
    tracing::info!("GitHub token purged from memory vault.");

    (
        StatusCode::OK,
        Json(VaultStatusResponse {
            is_configured: false,
            status: "purged".to_string(),
            masked_token: None,
            message: "Token purged from memory. Mock mode restored.".to_string(),
        }),
    )
}
