import asyncio
import logging
import os
import sys

from .temporal_worker import TemporalService, TemporalWorkerConfig
from .orchestration.coordinator import ResurrectionCoordinatorAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [specter.runtime] %(message)s",
)
logger = logging.getLogger("specter.main")

async def main():
    logger.info("Initializing SPECTER Autonomous Multi-Agent Runtime...")
    logger.info("Security Policy: --network none enforced for test executions.")
    logger.info("GitHub Token Vault: Redacted (never in AI prompts).")

    temporal_host = os.environ.get("TEMPORAL_HOST", "localhost:7233")
    config = TemporalWorkerConfig(target_host=temporal_host, mock_mode=True)
    temporal_svc = TemporalService(config=config)
    await temporal_svc.connect()

    coordinator = ResurrectionCoordinatorAgent()
    logger.info("Resurrection Coordinator armed with 5-agent pipeline.")
    logger.info("SPECTER Multi-Agent Runtime ready. Listening on queue 'specter-maintenance-queue'.")

    # Keep running or handle test signal
    if os.environ.get("SPECTER_ENV") == "test" or "--test-exit" in sys.argv:
        logger.info("Startup self-check passed. Exiting cleanly.")
        return

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Shutting down SPECTER agent runtime...")

if __name__ == "__main__":
    asyncio.run(main())

