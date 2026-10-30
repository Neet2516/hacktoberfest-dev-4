use axum::{
    body::Body,
    http::{Request, StatusCode},
    middleware::Next,
    response::Response,
};
use std::sync::atomic::{AtomicUsize, Ordering};

static REQUEST_COUNT: AtomicUsize = AtomicUsize::new(0);
const MAX_REQUESTS_PER_WINDOW: usize = 10000;

pub async fn rate_limiter(
    req: Request<Body>,
    next: Next,
) -> Result<Response, StatusCode> {
    let current = REQUEST_COUNT.fetch_add(1, Ordering::SeqCst);
    if current > MAX_REQUESTS_PER_WINDOW {
        return Err(StatusCode::TOO_MANY_REQUESTS);
    }

    Ok(next.run(req).await)
}

