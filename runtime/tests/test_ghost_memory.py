import unittest
from specter_runtime.memory.ghost_memory import GhostMemoryStore

class TestGhostMemorySubsystem(unittest.TestCase):
    def setUp(self):
        self.store = GhostMemoryStore()

    def test_add_and_query_by_tag(self):
        entry = self.store.add_entry(
            repository_id="repo-123",
            memory_type="CONVENTION",
            content="Use Result<T, CustomError> across all public crate APIs.",
            tags=["rust", "error-handling"],
        )
        self.assertEqual(entry.repository_id, "repo-123")

        results = self.store.query_by_tag("error-handling")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, entry.id)

    def test_cosine_similarity_retrieval(self):
        e1 = self.store.add_entry(
            repository_id="repo-1",
            memory_type="ARCH_DECISION",
            content="Database access isolated in repository layer",
            embedding=[1.0, 0.0, 0.0],
        )
        e2 = self.store.add_entry(
            repository_id="repo-1",
            memory_type="ARCH_DECISION",
            content="Use Tokio for async runtime",
            embedding=[0.0, 1.0, 0.0],
        )

        query = [0.9, 0.1, 0.0]
        results = self.store.retrieve_similar(query, top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, e1.id)

    def test_negative_test_case_recording(self):
        neg = self.store.record_negative_case(
            repository_id="repo-1",
            defect_desc="Index out of bounds on slice",
            failing_patch="diff --git a/lib.rs ...",
            reason="Did not guard against empty array",
        )
        self.assertIn("anti_pattern", neg.tags)
        self.assertEqual(neg.memory_type, "FAILURE_CASE")

    def test_prompt_augmentation(self):
        entry = self.store.add_entry(
            repository_id="repo-1",
            memory_type="CONVENTION",
            content="Never use unwrap() in library code",
            tags=["idiom"],
        )
        base_prompt = "Generate a fix for issue #4."
        augmented = self.store.augment_prompt_with_memory(base_prompt, [entry])

        self.assertIn("=== GHOST MEMORY CONTEXT ===", augmented)
        self.assertIn("Never use unwrap() in library code", augmented)

if __name__ == "__main__":
    unittest.main()
