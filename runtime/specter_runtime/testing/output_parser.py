import re
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class TestSummary:
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    success: bool = True
    failure_messages: List[str] = None

    def __post_init__(self):
        if self.failure_messages is None:
            self.failure_messages = []

class TestOutputParser:
    """Parses standard test framework output into a canonical TestSummary."""

    @classmethod
    def parse(cls, framework: str, stdout: str, stderr: str, exit_code: int) -> TestSummary:
        combined = f"{stdout}\n{stderr}"
        if exit_code != 0 and "timed out" in combined.lower():
            return TestSummary(
                total=0,
                passed=0,
                failed=1,
                skipped=0,
                success=False,
                failure_messages=["Test execution timed out in isolated sandbox."],
            )

        if framework == "cargo":
            # Cargo format: test result: ok. 5 passed; 0 failed; 0 ignored; ...
            match = re.search(r"test result: (ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored", combined)
            if match:
                passed = int(match.group(2))
                failed = int(match.group(3))
                ignored = int(match.group(4))
                return TestSummary(
                    total=passed + failed + ignored,
                    passed=passed,
                    failed=failed,
                    skipped=ignored,
                    success=(failed == 0 and exit_code == 0),
                    failure_messages=[f"Cargo test failure: {line}" for line in combined.splitlines() if "FAILED" in line and not line.startswith("test result:")][:5],
                )

        # Pytest / Unittest format: Ran X tests in Ys ... OK or FAILED (failures=Z)
        match_py = re.search(r"Ran (\d+) tests? in", combined)
        if match_py:
            total = int(match_py.group(1))
            fail_match = re.search(r"FAILED \((?:failures=(\d+))?(?:, )?(?:errors=(\d+))?\)", combined)
            failed = 0
            if fail_match:
                f_count = int(fail_match.group(1)) if fail_match.group(1) else 0
                e_count = int(fail_match.group(2)) if fail_match.group(2) else 0
                failed = f_count + e_count
            passed = total - failed
            return TestSummary(
                total=total,
                passed=passed,
                failed=failed,
                skipped=0,
                success=(failed == 0 and exit_code == 0),
                failure_messages=[line.strip() for line in combined.splitlines() if line.startswith("ERROR:") or line.startswith("FAIL:")][:5],
            )

        # Generic fallback
        success = (exit_code == 0)
        return TestSummary(
            total=1,
            passed=1 if success else 0,
            failed=0 if success else 1,
            skipped=0,
            success=success,
            failure_messages=[] if success else [f"Process exited with non-zero code {exit_code}"],
        )

