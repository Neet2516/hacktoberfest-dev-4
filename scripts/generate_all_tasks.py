import os
import re

os.makedirs('tasks/backlog', exist_ok=True)
os.makedirs('tasks/ready', exist_ok=True)

with open('tasks/TASK_INDEX.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

tasks = []
current_epic_title = ''
epic_map = {}

for line in lines:
    line = line.strip()
    if line.startswith('## EPIC'):
        current_epic_title = line.replace('## ', '').strip()
    elif line.startswith('| SPECTER-'):
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) >= 7:
            epic_code = parts[2]
            if epic_code not in epic_map and current_epic_title:
                epic_map[epic_code] = current_epic_title
            tasks.append({
                'id': parts[0],
                'title': parts[1],
                'epic_code': parts[2],
                'priority': parts[3],
                'status': parts[4],
                'owner': parts[5],
                'dependencies': parts[6]
            })

# Map epics to PRD functional requirements
prd_mapping = {
    'EPIC 01': ['FR-05', 'FR-14'],
    'EPIC 02': ['FR-02', 'FR-10', 'FR-14'],
    'EPIC 03': ['FR-01', 'FR-02', 'FR-03'],
    'EPIC 04': ['FR-03', 'FR-10'],
    'EPIC 05': ['FR-04', 'FR-13'],
    'EPIC 06': ['FR-05', 'FR-06'],
    'EPIC 07': ['FR-06'],
    'EPIC 08': ['FR-10'],
    'EPIC 09': ['FR-04', 'FR-05'],
    'EPIC 10': ['FR-07'],
    'EPIC 11': ['FR-08'],
    'EPIC 12': ['FR-09'],
    'EPIC 13': ['FR-05', 'FR-14'],
    'EPIC 14': ['FR-12', 'FR-13'],
    'EPIC 15': ['FR-11', 'FR-12'],
    'EPIC 16': ['FR-02', 'FR-09', 'FR-13'],
    'EPIC 17': ['FR-05', 'FR-09', 'FR-14'],
    'EPIC 18': ['FR-01', 'FR-12']
}

def generate_task_content(task):
    tid = task['id']
    title = task['title']
    epic_code = task['epic_code']
    epic_name = epic_map.get(epic_code, epic_code)
    priority = task['priority']
    status = task['status']
    owner = task['owner']
    deps = task['dependencies']
    frs = prd_mapping.get(epic_code, ['FR-05'])
    fr_str = ', '.join(frs)
    
    # Generate contextual technical specification
    tech_spec = f"""This task implements `{title}` as part of `{epic_name}`.
- **Architectural Scope**: Aligned with technical architecture specification in `docs/TECHNICAL_ARCHITECTURE.md`.
- **Target Subsystem**: Subsystem corresponding to {epic_name} ({owner}).
- **Design Constraints**: Adheres to strict modularity, memory safety, and least-privilege contracts defined in `agent/TOOL_CONTRACTS.md`."""

    # Generate contextual security considerations
    security = f"""- Strict validation of all inputs before processing.
- No secrets or credentials to be written to disk in plain text or emitted to logs.
- Adherence to SPECTER zero-trust boundary defined in `docs/THREAT_MODEL.md`."""
    if 'Docker' in title or 'Test' in title or 'isolated' in title.lower():
        security += "\n- Execute only inside rootless containers with network disabled (`--network none`)."
    if 'GitHub' in title or 'token' in title.lower() or 'PR' in title:
        security += "\n- GitHub tokens must be stored in secure vault and NEVER injected into LLM prompt context."
    if 'URL' in title or 'clone' in title.lower():
        security += "\n- Enforce SSRF prevention and URL sanitization. Block localhost and private IP ranges."

    # Implementation steps
    steps = f"""1. Review related architectural requirements in `docs/TECHNICAL_ARCHITECTURE.md`.
2. Implement core components and interfaces for `{title}`.
3. Wire integration hooks with dependent tasks ({deps}).
4. Implement comprehensive unit tests verifying normal and error edge cases.
5. Validate compliance with security and error-handling requirements."""

    # Acceptance criteria
    ac = f"""- [ ] Implementation of `{title}` is complete and functionally verified.
- [ ] Code adheres strictly to formatting, typing, and linting guidelines.
- [ ] Unit and integration test coverage meets or exceeds 85%.
- [ ] No regression or breaking changes introduced to dependent modules.
- [ ] Security checks and threat model mitigations verified."""

    # Definition of Done
    dod = f"""- [ ] Code implemented and peer-reviewed.
- [ ] Automated tests passing locally and in CI.
- [ ] Relevant documentation and architecture records updated.
- [ ] Verification evidence captured and attached to task record."""

    content = f"""# SPECTER Task: {tid}

---

## Task ID
`{tid}`

---

## Task Title
{title}

---

## Epic
{epic_name}

---

## Priority
{priority}

---

## Objective
Implement {title} to advance capabilities within {epic_name}. This component contributes directly to satisfying PRD requirements ({fr_str}) and maintaining system integrity and reproducibility.

---

## PRD Requirement Reference
{fr_str}

---

## Technical Specification
{tech_spec}

---

## Dependencies
{deps}

---

## Responsible Agent / Human Owner
{owner}

---

## Input Requirements
- Verified design specifications and predecessor artifacts from: {deps}.
- Relevant configuration files and schemas from `agent/schemas/` or environment settings.

---

## Expected Output
- Verified, compilable implementation of `{title}`.
- Automated tests covering functional and failure paths.
- Execution traces or logs proving correct behavior.

---

## Implementation Steps
{steps}

---

## Files Affected
- Modules associated with {epic_name} in backend, agent runtime, or frontend.
- Corresponding test suites and documentation references.

---

## Security Considerations
{security}

---

## Testing Requirements
- Unit tests validating component interfaces and logic boundaries.
- Negative test cases validating graceful failure and structured error emission.
- Integration tests ensuring proper handoff across system boundaries.

---

## Acceptance Criteria
{ac}

---

## Definition of Done
{dod}

---

## Current Status
{status}

---

## Blockers
None currently recorded in `memory/BLOCKERS.md` specifically blocking initialization.

---

## Evidence of Completion
Awaiting implementation and test execution.
"""
    return content

count = 0
for t in tasks:
    filepath = os.path.join('tasks/backlog', f"{t['id']}.md")
    task_content = generate_task_content(t)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(task_content.strip() + '\n')
    count += 1

print(f"Generated {count} task backlog files in tasks/backlog/")

# Initialize the 3 root tasks into tasks/ready/
ready_tasks = ['SPECTER-001', 'SPECTER-002', 'SPECTER-003']
for r_id in ready_tasks:
    src = os.path.join('tasks/backlog', f"{r_id}.md")
    dst = os.path.join('tasks/ready', f"{r_id}.md")
    with open(src, 'r', encoding='utf-8') as sf:
        c = sf.read()
    # update status to READY in file
    c = c.replace('## Current Status\nBACKLOG', '## Current Status\nREADY')
    with open(dst, 'w', encoding='utf-8') as df:
        df.write(c)
    print(f"Placed {r_id} in tasks/ready/")

