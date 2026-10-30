import os
import unittest
import asyncio
from specter_runtime.observability.metrics import MetricsCollector, AgentSpan
from specter_runtime.orchestration.coordinator import ResurrectionCoordinatorAgent, WorkflowStep

class TestObservabilityAndDemoScenario(unittest.TestCase):
    def test_metrics_collector(self):
        collector = MetricsCollector()
        collector.record_execution("ghost_repairer", duration_seconds=0.45, success=True)
        collector.record_execution("ghost_repairer", duration_seconds=0.55, success=True)
        collector.record_execution("adversarial_reviewer", duration_seconds=0.30, success=False)

        summary = collector.get_summary()
        self.assertEqual(summary["ghost_repairer"]["total_runs"], 2)
        self.assertEqual(summary["ghost_repairer"]["success_rate"], 1.0)
        self.assertEqual(summary["adversarial_reviewer"]["success_rate"], 0.0)

    def test_opentelemetry_traces_export(self):
        collector = MetricsCollector()
        span = AgentSpan(
            trace_id="tr_12345",
            span_id="sp_001",
            parent_span_id=None,
            name="archaeology_analysis",
            agent_id="repository_archaeologist",
            start_time=100.0,
            end_time=100.25,
            attributes={"repo": "abandoned_kv"},
        )
        collector.spans.append(span)
        exported = collector.export_opentelemetry_traces()
        self.assertEqual(len(exported), 1)
        self.assertEqual(exported[0]["name"], "archaeology_analysis")
        self.assertEqual(exported[0]["duration_ms"], 250.0)

    def test_e2e_demo_scenario(self):
        demo_repo_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "fixtures", "demo_repo"
        )
        self.assertTrue(os.path.exists(demo_repo_path))

        coordinator = ResurrectionCoordinatorAgent()
        pipeline = asyncio.run(
            coordinator.execute_resurrection_pipeline(
                pipeline_id="demo_pipeline_001",
                repository_url="https://github.com/demo/abandoned_kv",
                workspace_path=demo_repo_path,
                issue_number=1,
                issue_title="Buffer underflow in parse_config",
                issue_body="Empty slice causes crash in src/lib.rs",
            )
        )

        self.assertEqual(pipeline.current_step, WorkflowStep.PENDING_APPROVAL)
        self.assertIn("archaeology", pipeline.step_results)
        self.assertIn("investigation", pipeline.step_results)
        self.assertIn("repair", pipeline.step_results)
        self.assertIn("review", pipeline.step_results)
        self.assertIn("testing", pipeline.step_results)

if __name__ == "__main__":
    unittest.main()

