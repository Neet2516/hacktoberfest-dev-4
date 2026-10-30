import os
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class SymbolInfo:
    name: str
    kind: str  # "function", "class", "struct", "enum", "import"
    line_number: int
    signature: Optional[str] = None

@dataclass
class FileAnalysis:
    file_path: str
    language: str
    line_count: int
    symbols: List[SymbolInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    has_tests: bool = False

class CodeParser:
    """Multi-language code parser and symbol extractor for Repository Archaeology."""

    LANGUAGE_EXTENSIONS = {
        ".rs": "rust",
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".go": "go",
        ".c": "c",
        ".h": "c",
        ".cpp": "cpp",
    }

    @classmethod
    def detect_language(cls, file_path: str) -> Optional[str]:
        _, ext = os.path.splitext(file_path.lower())
        return cls.LANGUAGE_EXTENSIONS.get(ext)

    def parse_source(self, file_path: str, content: str) -> FileAnalysis:
        language = self.detect_language(file_path) or "unknown"
        lines = content.splitlines()
        line_count = len(lines)
        symbols = []
        imports = []
        has_tests = False

        if "test" in file_path.lower() or "spec" in file_path.lower():
            has_tests = True

        for idx, line in enumerate(lines, start=1):
            trimmed = line.strip()

            # Python
            if language == "python":
                if trimmed.startswith("import ") or trimmed.startswith("from "):
                    imports.append(trimmed)
                elif re.match(r"^def\s+([a-zA-Z0-9_]+)\s*\(", trimmed):
                    name = re.match(r"^def\s+([a-zA-Z0-9_]+)", trimmed).group(1)
                    symbols.append(SymbolInfo(name=name, kind="function", line_number=idx, signature=trimmed))
                    if name.startswith("test_"):
                        has_tests = True
                elif re.match(r"^class\s+([a-zA-Z0-9_]+)", trimmed):
                    name = re.match(r"^class\s+([a-zA-Z0-9_]+)", trimmed).group(1)
                    symbols.append(SymbolInfo(name=name, kind="class", line_number=idx, signature=trimmed))

            # Rust
            elif language == "rust":
                if trimmed.startswith("use "):
                    imports.append(trimmed)
                elif re.match(r"^(pub\s+)?(async\s+)?fn\s+([a-zA-Z0-9_]+)", trimmed):
                    m = re.match(r"^(pub\s+)?(async\s+)?fn\s+([a-zA-Z0-9_]+)", trimmed)
                    name = m.group(3)
                    symbols.append(SymbolInfo(name=name, kind="function", line_number=idx, signature=trimmed))
                elif re.match(r"^(pub\s+)?struct\s+([a-zA-Z0-9_]+)", trimmed):
                    m = re.match(r"^(pub\s+)?struct\s+([a-zA-Z0-9_]+)", trimmed)
                    name = m.group(2)
                    symbols.append(SymbolInfo(name=name, kind="struct", line_number=idx, signature=trimmed))
                elif "#[test]" in trimmed or "#[tokio::test]" in trimmed:
                    has_tests = True

            # TypeScript / JavaScript
            elif language in ["typescript", "javascript"]:
                if trimmed.startswith("import ") or trimmed.startswith("const ") and "require(" in trimmed:
                    imports.append(trimmed)
                elif re.match(r"^(export\s+)?(async\s+)?function\s+([a-zA-Z0-9_]+)", trimmed):
                    name = re.match(r"^(export\s+)?(async\s+)?function\s+([a-zA-Z0-9_]+)", trimmed).group(3)
                    symbols.append(SymbolInfo(name=name, kind="function", line_number=idx, signature=trimmed))
                elif re.match(r"^(export\s+)?(class|interface)\s+([a-zA-Z0-9_]+)", trimmed):
                    m = re.match(r"^(export\s+)?(class|interface)\s+([a-zA-Z0-9_]+)", trimmed)
                    symbols.append(SymbolInfo(name=m.group(3), kind=m.group(2), line_number=idx, signature=trimmed))

        return FileAnalysis(
            file_path=file_path,
            language=language,
            line_count=line_count,
            symbols=symbols,
            imports=imports,
            has_tests=has_tests,
        )
