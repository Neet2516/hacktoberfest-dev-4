import json
import time
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

@dataclass
class AgentSpan:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    name: str
    agent_id: str
    start_time: float
    end_time: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    status: str = "OK"

class MetricsCollector:
    """Collects and aggregates performance, latency, and success metrics across all agents."""

    def __init__(self):
        self.execution_counts: Dict[str, int] = {}
        self.failure_counts: Dict[str, int] = {}
        self.latencies: Dict[str, List[float]] = {}
        self.spans: List[AgentSpan] = []

    def record_execution(self, agent_id: str, duration_seconds: float, success: bool):
        self.execution_counts[agent_id] = self.execution_counts.get(agent_id, 0) + 1
        if not success:
            self.failure_counts[agent_id] = self.failure_counts.get(agent_id, 0) + 1
        if agent_id not in self.latencies:
            self.latencies[agent_id] = []
        self.latencies[agent_id].append(duration_seconds)

    def get_summary(self) -> Dict[str, Any]:
        summary = {}
        for agent_id, total in self.execution_counts.items():
            fails = self.failure_counts.get(agent_id, 0)
            lats = self.latencies.get(agent_id, [0.0])
            avg_lat = sum(lats) / len(lats) if lats else 0.0
            summary[agent_id] = {
                "total_runs": total,
                "success_rate": (total - fails) / total if total > 0 else 1.0,
                "avg_latency_ms": round(avg_lat * 1000, 2),
            }
        return summary

    def export_opentelemetry_traces(self) -> List[Dict[str, Any]]:
        return [
            {
                "trace_id": s.trace_id,
                "span_id": s.span_id,
                "parent_id": s.parent_span_id,
                "name": s.name,
                "agent_id": s.agent_id,
                "duration_ms": round(((s.end_time or time.time()) - s.start_time) * 1000, 2),
                "attributes": s.attributes,
                "status": s.status,
            }
            for s in self.spans
        ]
