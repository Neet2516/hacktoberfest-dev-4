import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

class OllamaClient:
    """Client for local open-weight Gemma 2 model inference via Ollama."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "gemma2:9b",
        mock_mode: bool = False,
        timeout_seconds: int = 60,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.mock_mode = mock_mode
        self.timeout_seconds = timeout_seconds

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        if self.mock_mode:
            return self._mock_response(prompt)

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system or "",
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return data.get("response", "")
                else:
                    return f"[Error: Ollama HTTP {response.status}]"
        except urllib.error.URLError as e:
            # Fallback to mock mode gracefully when offline
            return self._mock_response(prompt, fallback_reason=str(e))

    def _mock_response(self, prompt: str, fallback_reason: Optional[str] = None) -> str:
        p_lower = prompt.lower()
        if "archaeolog" in p_lower or "pattern" in p_lower:
            return json.dumps({
                "architecture_style": "Modular Service",
                "historical_insight": "Codebase shows disciplined maintainer intent with standard dependency patterns.",
                "preservation_notes": "Preserve existing public API and error handling structures."
            })
        elif "investigat" in p_lower or "root cause" in p_lower:
            return json.dumps({
                "root_cause": "Unhandled boundary condition on empty input slice.",
                "affected_symbol": "parse_config",
                "suggested_fix": "Add guard clause verifying input length prior to indexing."
            })
        elif "repair" in p_lower or "diff" in p_lower:
            return "diff --git a/src/lib.rs b/src/lib.rs\n--- a/src/lib.rs\n+++ b/src/lib.rs\n@@ -10,1 +10,3 @@\n+    if input.is_empty() { return Err(Error::Empty); }\n"
        elif "review" in p_lower:
            return json.dumps({
                "verdict": "APPROVED",
                "regression_risk": "LOW",
                "security_risk": "NONE",
                "findings": []
            })
        return "Deterministic SPECTER agent response."
