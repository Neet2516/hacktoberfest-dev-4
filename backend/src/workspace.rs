use std::fs;
use std::io;
use std::path::{Path, PathBuf};
use uuid::Uuid;

#[derive(Debug, Clone)]
pub struct WorkspaceManager {
    base_dir: PathBuf,
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

        // Enforce containment
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

    pub fn destroy_workspace(&self, workspace_path: &Path) -> io::Result<bool> {
        // Enforce strict containment check
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
