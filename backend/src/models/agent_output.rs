use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentOutputEntity {
    pub id: Uuid,
    pub task_id: String,
    pub agent_id: String,
    pub output_type: String,
    pub summary: String,
    pub data: serde_json::Value,
    pub evidence_refs: Vec<String>,
    pub created_at: String,
}

impl AgentOutputEntity {
    pub fn new(
        task_id: String,
        agent_id: String,
        output_type: String,
        summary: String,
        data: serde_json::Value,
        evidence_refs: Vec<String>,
    ) -> Self {
        Self {
            id: Uuid::new_v4(),
            task_id,
            agent_id,
            output_type,
            summary,
            data,
            evidence_refs,
            created_at: "2026-10-31T01:30:00Z".to_string(),
        }
    }
}
