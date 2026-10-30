use serde::{Deserialize, Serialize};
use sqlx::{FromRow, PgPool};
use std::fmt;
use uuid::Uuid;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum TaskStatus {
    Backlog,
    Ready,
    InProgress,
    Review,
    Completed,
    Blocked,
}

impl fmt::Display for TaskStatus {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TaskStatus::Backlog => write!(f, "BACKLOG"),
            TaskStatus::Ready => write!(f, "READY"),
            TaskStatus::InProgress => write!(f, "IN-PROGRESS"),
            TaskStatus::Review => write!(f, "REVIEW"),
            TaskStatus::Completed => write!(f, "COMPLETED"),
            TaskStatus::Blocked => write!(f, "BLOCKED"),
        }
    }
}

impl TaskStatus {
    pub fn from_str(s: &str) -> Option<Self> {
        match s {
            "BACKLOG" => Some(TaskStatus::Backlog),
            "READY" => Some(TaskStatus::Ready),
            "IN-PROGRESS" => Some(TaskStatus::InProgress),
            "REVIEW" => Some(TaskStatus::Review),
            "COMPLETED" => Some(TaskStatus::Completed),
            "BLOCKED" => Some(TaskStatus::Blocked),
            _ => None,
        }
    }

    pub fn can_transition_to(&self, next: &TaskStatus) -> bool {
        match (self, next) {
            // Standard forward lifecycle
            (TaskStatus::Backlog, TaskStatus::Ready) => true,
            (TaskStatus::Ready, TaskStatus::InProgress) => true,
            (TaskStatus::InProgress, TaskStatus::Review) => true,
            (TaskStatus::Review, TaskStatus::Completed) => true,
            
            // Rejection / iteration paths
            (TaskStatus::Review, TaskStatus::InProgress) => true,
            
            // Blockers & recovery
            (TaskStatus::InProgress, TaskStatus::Blocked) => true,
            (TaskStatus::Blocked, TaskStatus::InProgress) => true,
            (TaskStatus::Blocked, TaskStatus::Ready) => true,
            
            _ => false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct TaskEntity {
    pub id: String,
    pub repository_id: Option<Uuid>,
    pub title: String,
    pub epic: String,
    pub priority: String,
    pub status: String,
    pub assigned_agent: Option<String>,
}

impl TaskEntity {
    pub async fn create(
        pool: &PgPool,
        id: &str,
        repo_id: Option<Uuid>,
        title: &str,
        epic: &str,
        priority: &str,
    ) -> Result<Self, sqlx::Error> {
        let task = sqlx::query_as::<_, TaskEntity>(
            r#"
            INSERT INTO tasks (id, repository_id, title, epic, priority, status)
            VALUES ($1, $2, $3, $4, $5, 'BACKLOG')
            ON CONFLICT (id) DO UPDATE 
            SET title = EXCLUDED.title, updated_at = CURRENT_TIMESTAMP
            RETURNING id, repository_id, title, epic, priority, status, assigned_agent
            "#,
        )
        .bind(id)
        .bind(repo_id)
        .bind(title)
        .bind(epic)
        .bind(priority)
        .fetch_one(pool)
        .await?;

        Ok(task)
    }

    pub async fn transition(
        pool: &PgPool,
        id: &str,
        target_status: TaskStatus,
    ) -> Result<bool, Box<dyn std::error::Error + Send + Sync>> {
        let current_task = sqlx::query_as::<_, TaskEntity>(
            "SELECT id, repository_id, title, epic, priority, status, assigned_agent FROM tasks WHERE id = $1",
        )
        .bind(id)
        .fetch_optional(pool)
        .await?;

        let task = match current_task {
            Some(t) => t,
            None => return Err(format!("Task {} not found", id).into()),
        };

        let current_state = TaskStatus::from_str(&task.status)
            .ok_or_else(|| format!("Invalid current status in DB: {}", task.status))?;

        if !current_state.can_transition_to(&target_status) {
            return Err(format!(
                "Illegal task state transition: cannot transition from {} to {}",
                current_state, target_status
            )
            .into());
        }

        sqlx::query("UPDATE tasks SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2")
            .bind(target_status.to_string())
            .bind(id)
            .execute(pool)
            .await?;

        Ok(true)
    }
}
