import os
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class ReadmeInsights:
    title: str
    description: str
    badges: List[str] = field(default_factory=list)
    has_install_instructions: bool = False
    has_contributing_guide: bool = False
    last_documented_year: Optional[int] = None

@dataclass
class DependencyInventory:
    package_manager: str
    manifest_file: str
    dependencies: Dict[str, str] = field(default_factory=dict)
    dev_dependencies: Dict[str, str] = field(default_factory=dict)

@dataclass
class RepositoryContextReport:
    repo_name: str
    primary_languages: List[str]
    architecture_pattern: str
    build_system: str
    test_framework: Optional[str]
    dependencies: List[DependencyInventory]
    readme_insights: Optional[ReadmeInsights]
    historical_summary: str
    unresolved_smells: List[str] = field(default_factory=list)

class ReadmeAnalyzer:
    @staticmethod
    def analyze(content: str) -> ReadmeInsights:
        lines = content.splitlines()
        title = "Unknown Repository"
        description = ""
        badges = []
        has_install = False
        has_contrib = False
        years = []

        for line in lines:
            trimmed = line.strip()
            # Title
            if trimmed.startswith("# ") and title == "Unknown Repository":
                title = trimmed[2:].strip()
            # Badges
            if "![" in trimmed and "](" in trimmed:
                badges.append(trimmed)
            # Sections
            lower = trimmed.lower()
            if "install" in lower or "getting started" in lower or "setup" in lower:
                has_install = True
            if "contribut" in lower:
                has_contrib = True
            # Detect dates/years (e.g. 2018, 2021)
            for y_match in re.findall(r"\b(20[12][0-9])\b", trimmed):
                years.append(int(y_match))

        # Description: first non-header, non-badge paragraph
        for line in lines:
            trimmed = line.strip()
            if trimmed and not trimmed.startswith("#") and "![" not in trimmed:
                description = trimmed
                break

        last_year = max(years) if years else None
        return ReadmeInsights(
            title=title,
            description=description,
            badges=badges,
            has_install_instructions=has_install,
            has_contributing_guide=has_contrib,
            last_documented_year=last_year,
        )

class DependencyExtractor:
    @staticmethod
    def extract_from_manifest(file_name: str, content: str) -> Optional[DependencyInventory]:
        lower = file_name.lower()

        # Cargo.toml (Rust)
        if lower == "cargo.toml":
            deps = {}
            dev_deps = {}
            current_section = None
            for line in content.splitlines():
                trimmed = line.strip()
                if trimmed.startswith("[") and trimmed.endswith("]"):
                    current_section = trimmed.strip("[]")
                elif "=" in trimmed and not trimmed.startswith("#"):
                    parts = trimmed.split("=", 1)
                    k = parts[0].strip()
                    v = parts[1].strip().strip('"\'')
                    if current_section == "dependencies":
                        deps[k] = v
                    elif current_section in ["dev-dependencies", "build-dependencies"]:
                        dev_deps[k] = v
            return DependencyInventory(
                package_manager="cargo",
                manifest_file=file_name,
                dependencies=deps,
                dev_dependencies=dev_deps,
            )

        # package.json (Node/TS)
        elif lower == "package.json":
            import json
            try:
                data = json.loads(content)
                return DependencyInventory(
                    package_manager="npm",
                    manifest_file=file_name,
                    dependencies=data.get("dependencies", {}),
                    dev_dependencies=data.get("devDependencies", {}),
                )
            except Exception:
                pass

        # pyproject.toml / requirements.txt (Python)
        elif lower == "requirements.txt":
            deps = {}
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = re.split(r"[=><~]", line, 1)
                    deps[parts[0].strip()] = line
            return DependencyInventory(
                package_manager="pip",
                manifest_file=file_name,
                dependencies=deps,
                dev_dependencies={},
            )

        return None

class PatternDetector:
    @staticmethod
    def detect_pattern(files: List[str], languages: List[str]) -> str:
        files_lower = [f.lower() for f in files]
        if any("docker-compose" in f for f in files_lower) and any("service" in f for f in files_lower):
            return "Microservices / Containerized Mesh"
        if any("cli" in f or "main.rs" in f or "cmd/" in f for f in files_lower):
            return "CLI Application / Command Utility"
        if any("app/" in f or "pages/" in f or "src/app" in f for f in files_lower):
            return "Full-Stack Web Application"
        if "rust" in languages or "c" in languages:
            return "Systems Library / Core Crate"
        return "Modular Library"

