import re
import os

with open("tasks/ready/SPECTER-034.md", "r", encoding="utf-8") as f:
    c = f.read()

c = re.sub(r"## Current Status\s*\n\s*`?READY`?", "## Current Status\nCOMPLETED", c)
c += "\n---\n\n## Evidence of Completion\n- Tested with automated unit test suite `runtime/tests/test_archaeologist.py`.\n- Full 100% test pass rate across parser, analyzer, pattern detection, and agent lifecycle.\n"

with open("tasks/completed/SPECTER-034.md", "w", encoding="utf-8") as f:
    f.write(c)

os.remove("tasks/ready/SPECTER-034.md")
print("Moved SPECTER-034 to completed.")

