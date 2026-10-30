use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use http_body_util::BodyExt;
use serde_json::{json, Value};
use specter_backend::{create_router, WorkspaceManager};
use tower::ServiceExt;

#[tokio::test]
async fn test_valid_github_url_validation() {
    let app = create_router();

    let response = app
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/api/v1/repos/validate")
                .header("content-type", "application/json")
                .body(Body::from(
                    json!({ "url": "https://github.com/octocat/Spoon-Knife" }).to_string(),
                ))
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::OK);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let json: Value = serde_json::from_slice(&body).unwrap();

    assert_eq!(json["valid"], true);
    assert_eq!(json["owner"], "octocat");
    assert_eq!(json["name"], "Spoon-Knife");
    assert_eq!(json["canonical_url"], "https://github.com/octocat/Spoon-Knife");
}

#[tokio::test]
async fn test_invalid_ssrf_url_rejection() {
    let app = create_router();

    let response = app
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/api/v1/repos/validate")
                .header("content-type", "application/json")
                .body(Body::from(
                    json!({ "url": "http://127.0.0.1:8080/evil/repo" }).to_string(),
                ))
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::BAD_REQUEST);

    let body = response.into_body().collect().await.unwrap().to_bytes();
    let json: Value = serde_json::from_slice(&body).unwrap();

    assert_eq!(json["valid"], false);
    assert!(json["error"].as_str().unwrap().contains("Private and localhost"));
}

#[test]
fn test_workspace_manager_lifecycle() {
    let manager = WorkspaceManager::default_temp().unwrap();

    let (id, path) = manager.create_workspace("repo_test").unwrap();
    assert!(path.exists());
    assert!(path.starts_with(manager.base_directory()));

    let destroyed = manager.destroy_workspace(&path).unwrap();
    assert!(destroyed);
    assert!(!path.exists());
}
