import glob
import re

for pattern in ["tasks/backlog/SPECTER-*.md"]:
    for f in sorted(glob.glob(pattern)):
        content = open(f, encoding="utf-8").read()
        m_id = re.search(r"## Task ID\s*\n\s*`?(SPECTER-\d+)`?", content)
        m_ti = re.search(r"## Task Title\s*\n\s*([^\n]+)", content)
        m_ep = re.search(r"## Epic\s*\n\s*([^\n]+)", content)
        if m_id and m_ti and m_ep:
            print(f"{m_id.group(1)} | {m_ep.group(1)} | {m_ti.group(1)}")

