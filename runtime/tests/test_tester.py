import unittest
import asyncio
import tempfile
import os
from specter_runtime.context import AgentContext
from specter_runtime.message_bus import AgentMessageBus
from specter_runtime.testing.framework_detector import TestFrameworkDetector
from specter_runtime.testing.sandbox_runner import DockerTestSandbox, SandboxExecutionResult
from specter_runtime.testing.output_parser import TestOutputParser
from specter_runtime.testing.tester import TestEngineerAgent, VerificationReport

class MockSandbox(DockerTestSandbox):
    def __init__(self, exit_code=0, stdout="test result: ok. 5 passed; 0 failed; 0 ignored", stderr=""):
        super().__init__()
        self.mock_exit_code = exit_code
        self.mock_stdout = stdout
        self.mock_stderr = stderr

    def execute(self, workspace_path, test_cmd):
        return SandboxExecutionResult(
            exit_code=self.mock_exit_code,
            stdout=self.mock_stdout,
            stderr=self.mock_stderr,
        )

class TestIsolatedTestExecution(unittest.TestCase):
    def test_framework_detector(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test default / unknown
            cfg = TestFrameworkDetector.detect(tmp_dir)
            self.assertEqual(cfg.framework_name, "unknown")

            # Test Cargo detection
            cargo_file = os.path.join(tmp_dir, "Cargo.toml")
            with open(cargo_file, "w") as f:
                f.write("[package]\nname = 'test'")
            cfg = TestFrameworkDetector.detect(tmp_dir)
            self.assertEqual(cfg.framework_name, "cargo")
            self.assertEqual(cfg.command, ["cargo", "test"])

    def test_sandbox_docker_command_security_flags(self):
        sandbox = DockerTestSandbox(memory_limit="1g", cpu_limit="1.5")
        cmd = sandbox.build_docker_command("/workspace/repo", ["cargo", "test"])

        self.assertIn("--network", cmd)
        idx = cmd.index("--network")
        self.assertEqual(cmd[idx + 1], "none")
        self.assertIn("--security-opt", cmd)
        self.assertIn("no-new-privileges:true", cmd)
        self.assertIn("/workspace/repo:/workspace:ro", cmd)

    def test_output_parser_cargo(self):
        stdout = "running 5 tests\ntest test_foo ... ok\ntest result: ok. 5 passed; 0 failed; 0 ignored"
        summary = TestOutputParser.parse("cargo", stdout, "", 0)
        self.assertTrue(summary.success)
        self.assertEqual(summary.passed, 5)
        self.assertEqual(summary.failed, 0)
        self.assertEqual(summary.total, 5)

    def test_output_parser_cargo_failure(self):
        stdout = "test result: FAILED. 4 passed; 1 failed; 0 ignored"
        summary = TestOutputParser.parse("cargo", stdout, "", 101)
        self.assertFalse(summary.success)
        self.assertEqual(summary.passed, 4)
        self.assertEqual(summary.failed, 1)

    def test_output_parser_python_unittest(self):
        stdout = "Ran 10 tests in 0.05s\n\nOK"
        summary = TestOutputParser.parse("python_test", stdout, "", 0)
        self.assertTrue(summary.success)
        self.assertEqual(summary.total, 10)
        self.assertEqual(summary.passed, 10)

    def test_test_engineer_agent_success_flow(self):
        bus = AgentMessageBus()
        sandbox = MockSandbox(exit_code=0, stdout="test result: ok. 8 passed; 0 failed; 0 ignored")
        agent = TestEngineerAgent(message_bus=bus, sandbox=sandbox)

        with tempfile.TemporaryDirectory() as tmp_dir:
            with open(os.path.join(tmp_dir, "Cargo.toml"), "w") as f:
                f.write("[package]")

            context = AgentContext(
                task_id="test_run_101",
                repository_url="https://github.com/org/repo",
                workspace_path=tmp_dir,
            )

            result = asyncio.run(agent.run(context))
            self.assertEqual(result.status.value, "completed")
            self.assertTrue(result.data["verified"])
            self.assertEqual(result.data["passed_tests"], 8)

    def test_test_engineer_agent_failure_flow(self):
        bus = AgentMessageBus()
        sandbox = MockSandbox(exit_code=1, stdout="test result: FAILED. 2 passed; 1 failed; 0 ignored", stderr="assertion failed")
        agent = TestEngineerAgent(message_bus=bus, sandbox=sandbox)

        with tempfile.TemporaryDirectory() as tmp_dir:
            with open(os.path.join(tmp_dir, "Cargo.toml"), "w") as f:
                f.write("[package]")

            context = AgentContext(
                task_id="test_run_102",
                repository_url="https://github.com/org/repo",
                workspace_path=tmp_dir,
            )

            result = asyncio.run(agent.run(context))
            self.assertEqual(result.status.value, "failed")
            self.assertFalse(result.data["verified"])
            self.assertEqual(result.data["failed_tests"], 1)

if __name__ == "__main__":
    unittest.main()
