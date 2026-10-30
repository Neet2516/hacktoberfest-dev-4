use specter_backend::models::{AgentOutputEntity, AuditLogEntry};
use specter_backend::routes::ingestion::extract_repository_metadata;
use specter_backend::routes::{create_router, AppState};

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
async fn test_full_router_creation() {
    let _state = AppState::default();
    let app = create_router();
    assert!(!format!("{:?}", app).is_empty());
}
