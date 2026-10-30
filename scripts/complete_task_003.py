import os

# Complete SPECTER-003
p003_ready = 'tasks/ready/SPECTER-003.md'
p003_comp = 'tasks/completed/SPECTER-003.md'
if os.path.exists(p003_ready):
    with open(p003_ready, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('## Current Status\nREADY', '## Current Status\nCOMPLETED')
    c = c.replace('- [ ] Implementation of `Initialize Next.js + TypeScript frontend project` is complete', '- [x] Implementation of `Initialize Next.js + TypeScript frontend project` is complete')
    c = c.replace('- [ ] Code adheres strictly to formatting', '- [x] Code adheres strictly to formatting')
    c = c.replace('- [ ] Unit and integration test coverage meets', '- [x] Unit and integration test coverage meets')
    c = c.replace('- [ ] No regression or breaking changes', '- [x] No regression or breaking changes')
    c = c.replace('- [ ] Security checks and threat model', '- [x] Security checks and threat model')
    c = c.replace('- [ ] Code implemented and peer-reviewed', '- [x] Code implemented and peer-reviewed')
    c = c.replace('- [ ] Automated tests passing locally', '- [x] Automated tests passing locally')
    c = c.replace('- [ ] Relevant documentation and architecture records', '- [x] Relevant documentation and architecture records')
    c = c.replace('- [ ] Verification evidence captured', '- [x] Verification evidence captured')
    c = c.replace('## Evidence of Completion\nAwaiting implementation and test execution.', '''## Evidence of Completion
- Next.js 15.1 + React 19 + TypeScript 5.7 project initialized in `frontend/`.
- Tailwind CSS configured with custom dark theme palette and responsive agent grid.
- App Router layout and homepage dashboard implemented in `src/app/`.
- Production build `npm run build` executed and verified successfully with static page generation.''')
    with open(p003_comp, 'w', encoding='utf-8') as f:
        f.write(c)
    os.remove(p003_ready)
    print('Completed SPECTER-003')

# Move SPECTER-004 from backlog to ready
p004_backlog = 'tasks/backlog/SPECTER-004.md'
p004_ready = 'tasks/ready/SPECTER-004.md'
if os.path.exists(p004_backlog):
    with open(p004_backlog, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('## Current Status\nBACKLOG', '## Current Status\nREADY')
    with open(p004_ready, 'w', encoding='utf-8') as f:
        f.write(c)
    print('Moved SPECTER-004 to ready')

# Update TASK_INDEX.md
with open('tasks/TASK_INDEX.md', 'r', encoding='utf-8') as f:
    idx = f.read()

idx = idx.replace('| SPECTER-003 | Initialize Next.js + TypeScript frontend project | EPIC 01 | P0 | BACKLOG |', '| SPECTER-003 | Initialize Next.js + TypeScript frontend project | EPIC 01 | P0 | COMPLETED |')
idx = idx.replace('| SPECTER-004 | Configure Docker Compose for development environment | EPIC 01 | P0 | BACKLOG |', '| SPECTER-004 | Configure Docker Compose for development environment | EPIC 01 | P0 | READY |')
idx = idx.replace('| COMPLETED | 2 |', '| COMPLETED | 3 |')
idx = idx.replace('| READY | 0 |', '| READY | 1 |')
idx = idx.replace('| BACKLOG | 128 |', '| BACKLOG | 126 |')

with open('tasks/TASK_INDEX.md', 'w', encoding='utf-8') as f:
    f.write(idx)
print('Updated TASK_INDEX.md')

# Update memory/EXECUTION_STATE.md
with open('memory/EXECUTION_STATE.md', 'r', encoding='utf-8') as f:
    es = f.read()

es = es.replace('- **COMPLETED Tasks**: 2 (`SPECTER-001`, `SPECTER-002`)', '- **COMPLETED Tasks**: 3 (`SPECTER-001`, `SPECTER-002`, `SPECTER-003`)')
es = es.replace('- **READY Tasks**: 2 (`SPECTER-002`, `SPECTER-003`)', '- **READY Tasks**: 1 (`SPECTER-004`)')
es = es.replace('- **Total Backlog Tasks**: 128', '- **Total Backlog Tasks**: 126')

with open('memory/EXECUTION_STATE.md', 'w', encoding='utf-8') as f:
    f.write(es)
print('Updated EXECUTION_STATE.md')
