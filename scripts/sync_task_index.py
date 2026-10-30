import os
import glob
import re

completed_files = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob("tasks/completed/*.md")}
ready_files = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob("tasks/ready/*.md")}
inprogress_files = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob("tasks/in-progress/*.md")}

with open("tasks/TASK_INDEX.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    m = re.search(r"\|\s*\[?(SPECTER-\d+)\]?", line)
    if m:
        tid = m.group(1)
        if tid in completed_files:
            # Replace status column with COMPLETED
            # Format: | [SPECTER-001](...) | Title | Epic | Priority | Owner | Status |
            parts = line.split("|")
            if len(parts) >= 7:
                parts[6] = " COMPLETED "
                line = "|".join(parts)
        elif tid in ready_files:
            parts = line.split("|")
            if len(parts) >= 7:
                parts[6] = " READY "
                line = "|".join(parts)
        elif tid in inprogress_files:
            parts = line.split("|")
            if len(parts) >= 7:
                parts[6] = " IN-PROGRESS "
                line = "|".join(parts)
    new_lines.append(line)

with open("tasks/TASK_INDEX.md", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("TASK_INDEX.md synchronized successfully.")
