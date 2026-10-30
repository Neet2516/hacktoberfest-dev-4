import os
from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class TestFrameworkConfig:
    framework_name: str
    command: List[str]
    timeout_seconds: int = 60
    coverage_command: Optional[List[str]] = None

class TestFrameworkDetector:
    """Detects primary testing framework and configuration in a workspace."""

    FRAMEWORK_RULES = [
        ("Cargo.toml", "cargo", ["cargo", "test"]),
        ("pytest.ini", "pytest", ["python", "-m", "pytest"]),
        ("pyproject.toml", "python_test", ["python", "-m", "unittest", "discover"]),
        ("setup.py", "python_test", ["python", "-m", "unittest", "discover"]),
        ("package.json", "npm_test", ["npm", "test"]),
        ("go.mod", "go_test", ["go", "test", "./..."]),
        ("pom.xml", "maven_test", ["mvn", "test"]),
    ]

    @classmethod
    def detect(cls, workspace_path: str) -> TestFrameworkConfig:
        for indicator, name, cmd in cls.FRAMEWORK_RULES:
            indicator_path = os.path.join(workspace_path, indicator)
            if os.path.exists(indicator_path):
                return TestFrameworkConfig(framework_name=name, command=cmd)

        # Fallback default
        return TestFrameworkConfig(framework_name="unknown", command=["echo", "No known test framework detected"])

