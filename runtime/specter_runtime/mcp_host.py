import json
import os
from typing import Dict, Any, Callable, Optional, List

class ToolAccessDeniedError(PermissionError):
    pass

class ToolExecutionError(RuntimeError):
    pass

class MCPToolHost:
    """Manages tool registration, role-based tool authorization, and least-privilege execution."""

    ROLE_PERMISSIONS: Dict[str, List[str]] = {
        "repository_archaeologist": [
            "read_file", "list_files", "get_commit_history", "detect_framework"
        ],
        "issue_investigator": [
            "read_file", "list_files", "get_issue_details", "search_symbols"
        ],
        "ghost_repairer": [
            "read_file", "propose_diff", "validate_syntax"
        ],
        "adversarial_reviewer": [
            "read_file", "inspect_diff", "scan_security_rules"
        ],
        "test_engineer": [
            "execute_sandbox_test", "parse_test_results", "read_test_logs"
        ],
        "coordinator": [
            "route_message", "create_proposal", "query_status", "dispatch_task"
        ]
    }

    def __init__(self):
        self._tools: Dict[str, Callable[..., Any]] = {}

    def register_tool(self, name: str, func: Callable[..., Any]):
        self._tools[name] = func

    def can_agent_use_tool(self, agent_role: str, tool_name: str) -> bool:
        allowed = self.ROLE_PERMISSIONS.get(agent_role, [])
        return tool_name in allowed

    def invoke(self, agent_role: str, tool_name: str, **kwargs) -> Any:
        if not self.can_agent_use_tool(agent_role, tool_name):
            raise ToolAccessDeniedError(
                f"Security Violation: Agent role '{agent_role}' is not authorized to invoke tool '{tool_name}'."
            )
        if tool_name not in self._tools:
            # Emulated tool response
            return {"status": "success", "tool": tool_name, "arguments": kwargs}

        try:
            return self._tools[tool_name](**kwargs)
        except Exception as e:
            raise ToolExecutionError(f"Error executing tool '{tool_name}': {e}") from e

