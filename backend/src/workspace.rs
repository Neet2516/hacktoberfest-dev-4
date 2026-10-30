use std::fs;
use std::io;
use std::path::{Path, PathBuf};
use serde::{Deserialize, Serialize};
use tokio::process::Command;
use uuid::Uuid;

use crate::routes::ingestion::parse_and_validate_github_url;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GitCommitInfo {
    pub sha: String,
    pub author_name: String,
    pub author_email: String,
    pub date: String,
    pub message: String,
}

#[derive(Debug, Clone)]
pub struct WorkspaceManager {
    base_dir: PathBuf,
}

#[derive(Debug, thiserror::Error)]
pub enum WorkspaceError {
    #[error("IO error: {0}")]
    Io(#[from] io::Error),
    #[error("Invalid URL: {0}")]
    InvalidUrl(String),
    #[error("Git command failed: {0}")]
    GitFailed(String),
    #[error("Security violation: {0}")]
    Security(String),
}

impl WorkspaceManager {
    pub fn new<P: AsRef<Path>>(base_dir: P) -> io::Result<Self> {
        let base_path = base_dir.as_ref().to_path_buf();
        if !base_path.exists() {
            fs::create_dir_all(&base_path)?;
        }
        Ok(Self {
            base_dir: base_path,
        })
    }

    pub fn default_temp() -> io::Result<Self> {
        let temp_dir = std::env::temp_dir().join("specter_workspaces");
        Self::new(temp_dir)
    }

    pub fn create_workspace(&self, prefix: &str) -> io::Result<(Uuid, PathBuf)> {
        let id = Uuid::new_v4();
        let ws_path = self.base_dir.join(format!("{}_{}", prefix, id));

        if !ws_path.starts_with(&self.base_dir) {
            return Err(io::Error::new(
                io::ErrorKind::PermissionDenied,
                "Path traversal detected in workspace creation",
            ));
        }

        fs::create_dir_all(&ws_path)?;
        tracing::info!(workspace_id = %id, path = ?ws_path, "Created isolated workspace");
        Ok((id, ws_path))
    }

    pub async fn clone_repository(
        &self,
        raw_url: &str,
        depth: Option<u32>,
    ) -> Result<(Uuid, PathBuf, String), WorkspaceError> {
        let (_owner, name, canonical_url) =
            parse_and_validate_github_url(raw_url).map_err(WorkspaceError::InvalidUrl)?;

        let (ws_id, ws_path) = self.create_workspace(&name)?;
        let depth_val = depth.unwrap_or(100).to_string();

        tracing::info!(
            url = %canonical_url,
            workspace = ?ws_path,
            depth = %depth_val,
            "Executing isolated git clone"
        );

        let output = Command::new("git")
            .arg("clone")
            .arg("--depth")
            .arg(&depth_val)
            .arg(&canonical_url)
            .arg(&ws_path)
            .output()
            .await?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            let _ = self.destroy_workspace(&ws_path);
            return Err(WorkspaceError::GitFailed(format!(
                "git clone failed: {}",
                stderr.trim()
            )));
        }

        let sha_output = Command::new("git")
            .current_dir(&ws_path)
            .arg("rev-parse")
            .arg("HEAD")
            .output()
            .await?;

        let baseline_commit = if sha_output.status.success() {
            String::from_utf8_lossy(&sha_output.stdout).trim().to_string()
        } else {
            "unknown".to_string()
        };

        tracing::info!(
            workspace_id = %ws_id,
            commit = %baseline_commit,
            "Repository cloned successfully into workspace"
        );

        Ok((ws_id, ws_path, baseline_commit))
    }

    pub async fn extract_git_history(
        &self,
        workspace_path: &Path,
        max_commits: usize,
    ) -> Result<Vec<GitCommitInfo>, WorkspaceError> {
        if !workspace_path.starts_with(&self.base_dir) {
            return Err(WorkspaceError::Security(
                "Attempted to read git history outside designated workspace root".to_string(),
            ));
        }

        let output = Command::new("git")
            .current_dir(workspace_path)
            .arg("log")
            .arg(format!("-n{}", max_commits))
            .arg("--pretty=format:%H|%an|%ae|%aI|%s")
            .output()
            .await?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(WorkspaceError::GitFailed(format!(
                "git log failed: {}",
                stderr.trim()
            )));
        }

        let stdout = String::from_utf8_lossy(&output.stdout);
        let mut commits = Vec::new();

        for line in stdout.lines() {
            let parts: Vec<&str> = line.split('|').collect();
            if parts.len() >= 5 {
                commits.push(GitCommitInfo {
                    sha: parts[0].to_string(),
                    author_name: parts[1].to_string(),
                    author_email: parts[2].to_string(),
                    date: parts[3].to_string(),
                    message: parts[4..].join("|"),
                });
            }
        }

        Ok(commits)
    }

    pub fn destroy_workspace(&self, workspace_path: &Path) -> io::Result<bool> {
        if !workspace_path.starts_with(&self.base_dir) {
            return Err(io::Error::new(
                io::ErrorKind::PermissionDenied,
                "Cannot destroy workspace outside designated root directory",
            ));
        }

        if workspace_path.exists() {
            fs::remove_dir_all(workspace_path)?;
            tracing::info!(path = ?workspace_path, "Cleaned up isolated workspace");
            Ok(true)
        } else {
            Ok(false)
        }
    }

    pub fn base_directory(&self) -> &Path {
        &self.base_dir
    }
}

#[derive(Debug, Clone)]
pub struct VirtualPathMapper {
    workspace_id: Uuid,
    physical_root: PathBuf,
}

impl VirtualPathMapper {
    pub fn new(workspace_id: Uuid, physical_root: PathBuf) -> Self {
        Self {
            workspace_id,
            physical_root,
        }
    }

    pub fn to_virtual_uri(&self, physical_path: &Path) -> Result<String, WorkspaceError> {
        if let Ok(relative) = physical_path.strip_prefix(&self.physical_root) {
            let rel_str = relative.to_string_lossy().replace('\\', "/");
            Ok(format!("workspace://{}/{}", self.workspace_id, rel_str))
        } else {
            Err(WorkspaceError::Security(
                "Attempted to virtualize path outside workspace boundaries".to_string(),
            ))
        }
    }

    pub fn to_physical_path(&self, virtual_uri: &str) -> Result<PathBuf, WorkspaceError> {
        let prefix = format!("workspace://{}/", self.workspace_id);
        if let Some(relative_str) = virtual_uri.strip_prefix(&prefix) {
            let candidate = self.physical_root.join(relative_str);
            if candidate.starts_with(&self.physical_root) {
                Ok(candidate)
            } else {
                Err(WorkspaceError::Security(
                    "Path traversal detected in virtual URI".to_string(),
                ))
            }
        } else {
            Err(WorkspaceError::Security(
                "Virtual URI does not match active workspace ID".to_string(),
            ))
        }
    }
}
