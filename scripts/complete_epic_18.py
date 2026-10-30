import os
import re
import glob

task_ids = [
    "SPECTER-125", "SPECTER-126", "SPECTER-127", "SPECTER-128", "SPECTER-129", "SPECTER-130"
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
- Deployment and documentation completed for EPIC 18.
- Production compose manifest created (`docker-compose.prod.yml`).
- Runbooks and developer guides authored in `docs/` (`DEPLOYMENT_RUNBOOK.md`, `API_REFERENCE.md`, `AGENT_DEVELOPER_GUIDE.md`, `SYSTEM_OPERATOR_GUIDE.md`, `DEMO_GUIDE.md`).
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
