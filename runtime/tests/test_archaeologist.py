import unittest
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from specter_runtime.archaeology.analyzer import (
    ReadmeAnalyzer,
    DependencyExtractor,
    PatternDetector,
)
from specter_runtime.llm.client import OllamaClient
from specter_runtime.agents.archaeologist import RepositoryArchaeologistAgent
from specter_runtime.context import AgentContext, AgentTaskState
from specter_runtime.message_bus import AgentMessageBus

class TestArchaeologySubsystem(unittest.TestCase):
    def test_readme_analyzer(self):
        readme_md = """# My Project
[![Build](https://img.shields.io/badge/build-passing-green)](https://example.com)

A high-performance system library for parsing binary protocols.

## Installation
Run `cargo install my_project`

## Contributing
Please see CONTRIBUTING.md. Copyright 2021.
"""
        insights = ReadmeAnalyzer.analyze(readme_md)
        self.assertEqual(insights.title, "My Project")
        self.assertIn("high-performance system library", insights.description)
        self.assertTrue(insights.has_install_instructions)
        self.assertTrue(insights.has_contributing_guide)
        self.assertEqual(insights.last_documented_year, 2021)

    def test_cargo_dependency_extractor(self):
        cargo_toml = """[package]
name = "demo"
version = "0.1.0"

[dependencies]
serde = "1.0"
tokio = "1.0"

[dev-dependencies]
tempfile = "3.0"
"""
        dep_inv = DependencyExtractor.extract_from_manifest("Cargo.toml", cargo_toml)
        self.assertIsNotNone(dep_inv)
        self.assertEqual(dep_inv.package_manager, "cargo")
        self.assertIn("serde", dep_inv.dependencies)
        self.assertIn("tempfile", dep_inv.dev_dependencies)

    def test_pattern_detector(self):
        files = ["src/main.rs", "src/cli.rs", "Cargo.toml"]
        pattern = PatternDetector.detect_pattern(files, ["rust"])
        self.assertIn("CLI", pattern)

    def test_ollama_client_generation(self):
        client = OllamaClient(mock_mode=True)
        response = client.generate("Analyze archaeology of this repository")
        self.assertIn("Modular Service", response)

    def test_archaeologist_agent_execution(self):
        bus = AgentMessageBus()
        client = OllamaClient(mock_mode=True)
        agent = RepositoryArchaeologistAgent(message_bus=bus, ollama_client=client)

        ctx = AgentContext(
            task_id="SPECTER-033",
            repository_url="https://github.com/example/abandoned-repo",
            workspace_path="/nonexistent/mock_ws",
        )

        result = asyncio.run(agent.run(ctx))
        self.assertEqual(result.status, AgentTaskState.COMPLETED)
        self.assertEqual(result.agent_id, "repository_archaeologist")
        
        messages = bus.get_task_messages("SPECTER-033")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message_type, "repository_context")

if __name__ == "__main__":
    unittest.main()

