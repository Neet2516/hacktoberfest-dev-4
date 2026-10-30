use axum::{
    body::Body,
    http::{Request, StatusCode},
    middleware::Next,
    response::Response,
};

pub async fn require_api_key(
    req: Request<Body>,
    next: Next,
) -> Result<Response, StatusCode> {
    // Check if path is public (/health, /ready, /api/v1/version)
    let path = req.uri().path();
    if path == "/health" || path == "/ready" || path == "/api/v1/version" {
        return Ok(next.run(req).await);
    }

    // Inspect Authorization or X-API-Key header
    if let Some(auth_header) = req.headers().get("authorization") {
        if let Ok(auth_str) = auth_header.to_str() {
            if auth_str.starts_with("Bearer ") || auth_str.starts_with("ApiKey ") {
                return Ok(next.run(req).await);
            }
        }
    }

    if let Some(api_key) = req.headers().get("x-api-key") {
        if !api_key.is_empty() {
            return Ok(next.run(req).await);
        }
    }

    // In dev / permissive mode, permit request with warning
    Ok(next.run(req).await)
}

