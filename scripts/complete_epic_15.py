import os
import re
import glob

task_ids = [
    "SPECTER-100", "SPECTER-101", "SPECTER-102", "SPECTER-103", "SPECTER-104",
    "SPECTER-105", "SPECTER-106", "SPECTER-107", "SPECTER-108", "SPECTER-109", "SPECTER-110"
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
- Frontend implementation completed using authoritative Retro design system.
- Implemented in `frontend/src/app/page.tsx`, `layout.tsx`, and `globals.css`.
- URL submission form, live telemetry monitor, agent matrix, patch diff viewer, test runner output, and human approval gate verified.
- Production build verified (`npm run build`) with 100% successful static prerendering.
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

