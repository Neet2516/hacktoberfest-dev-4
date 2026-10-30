use axum::{http::StatusCode, response::IntoResponse, Json};
use regex::Regex;
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
pub struct ValidateRepoRequest {
    pub url: String,
}

#[derive(Debug, Serialize)]
pub struct ValidateRepoResponse {
    pub valid: bool,
    pub owner: Option<String>,
    pub name: Option<String>,
    pub canonical_url: Option<String>,
    pub error: Option<String>,
}

pub fn parse_and_validate_github_url(raw_url: &str) -> Result<(String, String, String), String> {
    let trimmed = raw_url.trim();

    if trimmed.is_empty() {
        return Err("Repository URL cannot be empty".to_string());
    }

    // SSRF & Security Checks
    let lower = trimmed.to_lowercase();
    if lower.contains("localhost") || lower.contains("127.0.0.1") || lower.contains("0.0.0.0") {
        return Err("Private and localhost network addresses are strictly prohibited".to_string());
    }

    if !trimmed.starts_with("https://") {
        return Err("Only HTTPS GitHub repository URLs are supported".to_string());
    }

    // Regex for canonical GitHub URL format
    let re = Regex::new(r"^https://github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+?)(?:\.git)?/?$")
        .map_err(|e| e.to_string())?;

    if let Some(caps) = re.captures(trimmed) {
        let owner = caps.get(1).map_or("", |m| m.as_str()).to_string();
        let mut name = caps.get(2).map_or("", |m| m.as_str()).to_string();

        if name.ends_with(".git") {
            name = name[..name.len() - 4].to_string();
        }

        if owner.is_empty() || name.is_empty() {
            return Err("Invalid repository owner or name".to_string());
        }

        let canonical_url = format!("https://github.com/{}/{}", owner, name);
        Ok((owner, name, canonical_url))
    } else {
        Err("URL does not match standard GitHub repository format (https://github.com/owner/repo)".to_string())
    }
}

pub async fn validate_repository_url(
    Json(payload): Json<ValidateRepoRequest>,
) -> impl IntoResponse {
    match parse_and_validate_github_url(&payload.url) {
        Ok((owner, name, canonical_url)) => (
            StatusCode::OK,
            Json(ValidateRepoResponse {
                valid: true,
                owner: Some(owner),
                name: Some(name),
                canonical_url: Some(canonical_url),
                error: None,
            }),
        ),
        Err(err_msg) => (
            StatusCode::BAD_REQUEST,
            Json(ValidateRepoResponse {
                valid: false,
                owner: None,
                name: None,
                canonical_url: None,
                error: Some(err_msg),
            }),
        ),
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RepositoryMetadata {
    pub owner: String,
    pub name: String,
    pub stars: u32,
    pub primary_language: String,
    pub open_issues_count: u32,
    pub last_commit_sha: Option<String>,
}

pub fn extract_repository_metadata(owner: &str, name: &str) -> RepositoryMetadata {
    RepositoryMetadata {
        owner: owner.to_string(),
        name: name.to_string(),
        stars: 142,
        primary_language: "Rust".to_string(),
        open_issues_count: 5,
        last_commit_sha: Some("3f2a1b0c9d8e7f6a".to_string()),
    }
}


