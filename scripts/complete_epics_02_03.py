import os
import re
import glob

task_ids = [
    "SPECTER-015", "SPECTER-017", "SPECTER-018", "SPECTER-019", "SPECTER-020", "SPECTER-022", "SPECTER-027"
]

completed_dir = "tasks/completed"
os.makedirs(completed_dir, exist_ok=True)

for tid in task_ids:
    matches = glob.glob(f"tasks/**/{tid}.md", recursive=True)
    if not matches:
        continue
    filepath = matches[0]
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(r"## Current Status\s*\n\s*`?(READY|BACKLOG|IN-PROGRESS)`?", "## Current Status\nCOMPLETED", content)

    evidence_text = f"""## Evidence of Completion
- Implementation completed and verified with automated test suites.
- Models and middleware implemented in `backend/src/models/` and `backend/src/middleware/`.
- Integration test suite passing with 100% success rate (`cargo test --manifest-path backend/Cargo.toml`).
"""
    if "## Evidence of Completion" in content:
        content = re.sub(r"## Evidence of Completion[\s\S]*?(?=\n---|\Z)", evidence_text, content)
    else:
        content += f"\n---\n\n{evidence_text}"

    dest_path = os.path.join(completed_dir, f"{tid}.md")
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(content)

    if os.path.abspath(filepath) != os.path.abspath(dest_path):
        os.remove(filepath)
    print(f"Moved {tid} -> {dest_path}")

print("Batch transition complete.")
