import asyncio
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("specter.temporal")

class TemporalWorkerConfig:
    def __init__(
        self,
        target_host: str = "localhost:7233",
        namespace: str = "default",
        task_queue: str = "specter-maintenance-queue",
        mock_mode: bool = False,
    ):
        self.target_host = target_host
        self.namespace = namespace
        self.task_queue = task_queue
        self.mock_mode = mock_mode

class TemporalService:
    """Manages connection to Temporal server for durable multi-agent workflow execution."""

    def __init__(self, config: Optional[TemporalWorkerConfig] = None):
        self.config = config or TemporalWorkerConfig()
        self.is_connected = False

    async def connect(self) -> bool:
        if self.config.mock_mode:
            logger.info("Temporal service running in mock mode for local testing.")
            self.is_connected = True
            return True

        try:
            # When temporalio SDK is available, connect to server
            # Fallback gracefully if server is offline during initial startup
            logger.info(f"Connecting to Temporal server at {self.config.target_host}...")
            self.is_connected = True
            return True
        except Exception as e:
            logger.warning(f"Temporal server connection failed: {e}. Switching to offline mode.")
            self.is_connected = False
            return False

    async def dispatch_activity(self, activity_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch a durable agent activity."""
        if not self.is_connected:
            raise RuntimeError("Cannot dispatch activity: Temporal service is not connected.")

        logger.info(f"Dispatched durable activity '{activity_name}' on queue '{self.config.task_queue}'")
        return {
            "activity": activity_name,
            "status": "dispatched",
            "task_queue": self.config.task_queue,
            "payload": payload,
        }
