use serde::{Deserialize, Serialize};
use sqlx::{FromRow, PgPool};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Repository {
    pub id: Uuid,
    pub url: String,
    pub owner: String,
    pub name: String,
    pub default_branch: String,
    pub baseline_commit: Option<String>,
    pub primary_language: Option<String>,
    pub status: String,
}

#[derive(Debug, Deserialize)]
pub struct CreateRepositoryDto {
    pub url: String,
    pub owner: String,
    pub name: String,
    pub default_branch: Option<String>,
}

impl Repository {
    pub async fn create(pool: &PgPool, dto: CreateRepositoryDto) -> Result<Self, sqlx::Error> {
        let default_branch = dto.default_branch.unwrap_or_else(|| "main".to_string());
        
        let repo = sqlx::query_as::<_, Repository>(
            r#"
            INSERT INTO repositories (url, owner, name, default_branch, status)
            VALUES ($1, $2, $3, $4, 'ingested')
            ON CONFLICT (url) DO UPDATE 
            SET updated_at = CURRENT_TIMESTAMP
            RETURNING id, url, owner, name, default_branch, baseline_commit, primary_language, status
            "#,
        )
        .bind(&dto.url)
        .bind(&dto.owner)
        .bind(&dto.name)
        .bind(&default_branch)
        .fetch_one(pool)
        .await?;

        Ok(repo)
    }

    pub async fn find_by_id(pool: &PgPool, id: Uuid) -> Result<Option<Self>, sqlx::Error> {
        sqlx::query_as::<_, Repository>(
            r#"
            SELECT id, url, owner, name, default_branch, baseline_commit, primary_language, status
            FROM repositories
            WHERE id = $1
            "#,
        )
        .bind(id)
        .fetch_optional(pool)
        .await
    }

    pub async fn find_by_url(pool: &PgPool, url: &str) -> Result<Option<Self>, sqlx::Error> {
        sqlx::query_as::<_, Repository>(
            r#"
            SELECT id, url, owner, name, default_branch, baseline_commit, primary_language, status
            FROM repositories
            WHERE url = $1
            "#,
        )
        .bind(url)
        .fetch_optional(pool)
        .await
    }

    pub async fn update_status(pool: &PgPool, id: Uuid, status: &str) -> Result<bool, sqlx::Error> {
        let rows_affected = sqlx::query(
            r#"
            UPDATE repositories
            SET status = $1, updated_at = CURRENT_TIMESTAMP
            WHERE id = $2
            "#,
        )
        .bind(status)
        .bind(id)
        .execute(pool)
        .await?
        .rows_affected();

        Ok(rows_affected > 0)
    }
}
