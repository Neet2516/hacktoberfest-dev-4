import unittest
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from specter_runtime.temporal_worker import TemporalService, TemporalWorkerConfig

class TestTemporalService(unittest.TestCase):
    def test_mock_connection(self):
        config = TemporalWorkerConfig(mock_mode=True)
        service = TemporalService(config)

        connected = asyncio.run(service.connect())
        self.assertTrue(connected)
        self.assertTrue(service.is_connected)

    def test_activity_dispatch(self):
        config = TemporalWorkerConfig(mock_mode=True, task_queue="test-queue")
        service = TemporalService(config)
        asyncio.run(service.connect())

        result = asyncio.run(
            service.dispatch_activity(
                "execute_archaeology",
                {"task_id": "SPECTER-006", "repo_url": "https://github.com/example/repo"}
            )
        )

        self.assertEqual(result["activity"], "execute_archaeology")
        self.assertEqual(result["status"], "dispatched")
        self.assertEqual(result["task_queue"], "test-queue")

if __name__ == "__main__":
    unittest.main()

