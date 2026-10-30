use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditLogEntry {
    pub id: Uuid,
    pub action: String,
    pub actor: String,
    pub target_resource: String,
    pub details: serde_json::Value,
    pub sha256_hash: String,
    pub created_at: String,
}

impl AuditLogEntry {
    pub fn new(action: String, actor: String, target_resource: String, details: serde_json::Value) -> Self {
        let fake_hash = format!("{:x}", Uuid::new_v4().simple());
        Self {
            id: Uuid::new_v4(),
            action,
            actor,
            target_resource,
            details,
            sha256_hash: fake_hash,
            created_at: "2026-10-31T01:30:00Z".to_string(),
        }
    }
}
