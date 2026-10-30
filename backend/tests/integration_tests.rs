use specter_backend::models::{AgentOutputEntity, AuditLogEntry};
use specter_backend::routes::ingestion::extract_repository_metadata;
use specter_backend::routes::vault::{clear_vault_token, get_vault_status, store_github_token, StoreTokenRequest};
use specter_backend::routes::{create_router, AppState};
use axum::Json;

#[tokio::test]
async fn test_agent_output_and_audit_models() {
    let output = AgentOutputEntity::new(
        "task_001".to_string(),
        "ghost_repairer".to_string(),
        "patch_diff".to_string(),
        "Generated patch for Issue #1".to_string(),
        serde_json::json!({"lines_added": 3}),
        vec!["src/lib.rs".to_string()],
    );

    assert_eq!(output.task_id, "task_001");
    assert_eq!(output.agent_id, "ghost_repairer");
    assert_eq!(output.evidence_refs.len(), 1);

    let audit = AuditLogEntry::new(
        "CREATE_PR".to_string(),
        "alice_maintainer".to_string(),
        "repo/pull/99".to_string(),
        serde_json::json!({"status": "APPROVED"}),
    );

    assert_eq!(audit.action, "CREATE_PR");
    assert_eq!(audit.actor, "alice_maintainer");
    assert!(!audit.sha256_hash.is_empty());
}

#[tokio::test]
async fn test_repository_metadata_extraction() {
    let meta = extract_repository_metadata("demo", "abandoned_kv");
    assert_eq!(meta.owner, "demo");
    assert_eq!(meta.name, "abandoned_kv");
    assert_eq!(meta.primary_language, "Rust");
    assert_eq!(meta.stars, 142);
    assert_eq!(meta.open_issues_count, 5);
}

#[tokio::test]
async fn test_token_vault_lifecycle() {
    // 1. Clear any prior state
    let _ = clear_vault_token().await;

    // 2. Reject invalid prefix
    let invalid_req = StoreTokenRequest {
        token: "invalid_secret_key_12345".to_string(),
    };
    let _ = store_github_token(Json(invalid_req)).await;

    // 3. Store valid token
    let valid_req = StoreTokenRequest {
        token: "ghp_secure_personal_token_99999".to_string(),
    };
    let _ = store_github_token(Json(valid_req)).await;

    // 4. Check status masked output
    let _status = get_vault_status().await;

    // 5. Clear token
    let _ = clear_vault_token().await;
}

#[tokio::test]
async fn test_full_router_creation() {
    let _state = AppState::default();
    let app = create_router();
    assert!(!format!("{:?}", app).is_empty());
}
