import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

@dataclass
class MemoryEntry:
    id: str
    repository_id: str
    memory_type: str  # "CONVENTION", "ARCH_DECISION", "FAILURE_CASE", "IDIOLECT"
    content: str
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class GhostMemoryStore:
    """Manages long-term repository memory, semantic embedding retrieval, and negative test caching."""

    def __init__(self):
        self.entries: Dict[str, MemoryEntry] = {}

    def add_entry(
        self,
        repository_id: str,
        memory_type: str,
        content: str,
        tags: Optional[List[str]] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryEntry:
        entry_id = str(uuid.uuid4())
        entry = MemoryEntry(
            id=entry_id,
            repository_id=repository_id,
            memory_type=memory_type,
            content=content,
            tags=tags or [],
            embedding=embedding,
            metadata=metadata or {},
        )
        self.entries[entry_id] = entry
        return entry

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = math.sqrt(sum(a * a for a in vec1))
        norm_b = math.sqrt(sum(b * b for b in vec2))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def retrieve_similar(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        memory_type: Optional[str] = None,
    ) -> List[MemoryEntry]:
        scored = []
        for entry in self.entries.values():
            if memory_type and entry.memory_type != memory_type:
                continue
            if entry.embedding:
                score = self._cosine_similarity(query_embedding, entry.embedding)
                scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:top_k]]

    def query_by_tag(self, tag: str) -> List[MemoryEntry]:
        return [e for e in self.entries.values() if tag in e.tags]

    def record_negative_case(self, repository_id: str, defect_desc: str, failing_patch: str, reason: str) -> MemoryEntry:
        """Records a rejected patch or known defect to prevent regression recurrence."""
        return self.add_entry(
            repository_id=repository_id,
            memory_type="FAILURE_CASE",
            content=f"Defect: {defect_desc}\nRejected Patch:\n{failing_patch}\nReason: {reason}",
            tags=["negative_case", "anti_pattern"],
            metadata={"defect": defect_desc, "reason": reason},
        )

    def augment_prompt_with_memory(self, prompt: str, memory_entries: List[MemoryEntry]) -> str:
        if not memory_entries:
            return prompt

        memory_block = "\n".join([f"- [{e.memory_type}] {e.content}" for e in memory_entries])
        return (
            f"{prompt}\n\n"
            f"=== GHOST MEMORY CONTEXT ===\n"
            f"Preserve existing author conventions and avoid known failures:\n"
            f"{memory_block}\n"
            f"==========================="
        )

