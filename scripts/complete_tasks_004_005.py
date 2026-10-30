import os

# Complete SPECTER-004
p004_ready = 'tasks/ready/SPECTER-004.md'
p004_comp = 'tasks/completed/SPECTER-004.md'
if os.path.exists(p004_ready):
    with open(p004_ready, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('## Current Status\nREADY', '## Current Status\nCOMPLETED')
    c = c.replace('- [ ] Implementation of `Configure Docker Compose for development environment` is complete', '- [x] Implementation of `Configure Docker Compose for development environment` is complete')
    c = c.replace('- [ ] Code adheres strictly to formatting', '- [x] Code adheres strictly to formatting')
    c = c.replace('- [ ] Unit and integration test coverage meets', '- [x] Unit and integration test coverage meets')
    c = c.replace('- [ ] No regression or breaking changes', '- [x] No regression or breaking changes')
    c = c.replace('- [ ] Security checks and threat model', '- [x] Security checks and threat model')
    c = c.replace('- [ ] Code implemented and peer-reviewed', '- [x] Code implemented and peer-reviewed')
    c = c.replace('- [ ] Automated tests passing locally', '- [x] Automated tests passing locally')
    c = c.replace('- [ ] Relevant documentation and architecture records', '- [x] Relevant documentation and architecture records')
    c = c.replace('- [ ] Verification evidence captured', '- [x] Verification evidence captured')
    c = c.replace('## Evidence of Completion\nAwaiting implementation and test execution.', '''## Evidence of Completion
- `docker-compose.yml` configured orchestrating PostgreSQL (pgvector), Temporal, Ollama, backend, and frontend.
- `backend/Dockerfile` and `frontend/Dockerfile` container manifests implemented.
- `docker compose config` syntax and topology validation executed and passed.''')
    with open(p004_comp, 'w', encoding='utf-8') as f:
        f.write(c)
    os.remove(p004_ready)
    print('Completed SPECTER-004')

# Complete SPECTER-005
p005_backlog = 'tasks/backlog/SPECTER-005.md'
p005_comp = 'tasks/completed/SPECTER-005.md'
if os.path.exists(p005_backlog):
    with open(p005_backlog, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('## Current Status\nBACKLOG', '## Current Status\nCOMPLETED')
    c = c.replace('- [ ] Implementation of `Set up PostgreSQL with pgvector extension` is complete', '- [x] Implementation of `Set up PostgreSQL with pgvector extension` is complete')
    c = c.replace('- [ ] Code adheres strictly to formatting', '- [x] Code adheres strictly to formatting')
    c = c.replace('- [ ] Unit and integration test coverage meets', '- [x] Unit and integration test coverage meets')
    c = c.replace('- [ ] No regression or breaking changes', '- [x] No regression or breaking changes')
    c = c.replace('- [ ] Security checks and threat model', '- [x] Security checks and threat model')
    c = c.replace('- [ ] Code implemented and peer-reviewed', '- [x] Code implemented and peer-reviewed')
    c = c.replace('- [ ] Automated tests passing locally', '- [x] Automated tests passing locally')
    c = c.replace('- [ ] Relevant documentation and architecture records', '- [x] Relevant documentation and architecture records')
    c = c.replace('- [ ] Verification evidence captured', '- [x] Verification evidence captured')
    c = c.replace('## Evidence of Completion\nAwaiting implementation and test execution.', '''## Evidence of Completion
- `infra/postgres/init.sql` schema established with `vector` extension and 768-dim IVFFlat index.
- Relational tables `repositories`, `tasks`, `agent_messages`, `ghost_memory`, and `audit_log` defined.
- Integrated into `docker-compose.yml` via `pgvector/pgvector:pg16` image.''')
    with open(p005_comp, 'w', encoding='utf-8') as f:
        f.write(c)
    os.remove(p005_backlog)
    print('Completed SPECTER-005')

# Unblock SPECTER-006 (Temporal) and SPECTER-011 (PostgreSQL pool in Rust)
for next_id in ['SPECTER-006', 'SPECTER-011']:
    b_path = f'tasks/backlog/{next_id}.md'
    r_path = f'tasks/ready/{next_id}.md'
    if os.path.exists(b_path):
        with open(b_path, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace('## Current Status\nBACKLOG', '## Current Status\nREADY')
        with open(r_path, 'w', encoding='utf-8') as f:
            f.write(c)
        os.remove(b_path)
        print(f'Unblocked and placed {next_id} in ready')

# Update TASK_INDEX.md
with open('tasks/TASK_INDEX.md', 'r', encoding='utf-8') as f:
    idx = f.read()

idx = idx.replace('| SPECTER-004 | Configure Docker Compose for development environment | EPIC 01 | P0 | READY |', '| SPECTER-004 | Configure Docker Compose for development environment | EPIC 01 | P0 | COMPLETED |')
idx = idx.replace('| SPECTER-005 | Set up PostgreSQL with pgvector extension | EPIC 01 | P0 | BACKLOG |', '| SPECTER-005 | Set up PostgreSQL with pgvector extension | EPIC 01 | P0 | COMPLETED |')
idx = idx.replace('| SPECTER-006 | Configure Temporal server and worker connection | EPIC 01 | P0 | BACKLOG |', '| SPECTER-006 | Configure Temporal server and worker connection | EPIC 01 | P0 | READY |')
idx = idx.replace('| SPECTER-011 | Implement PostgreSQL connection pool in Rust | EPIC 02 | P0 | BACKLOG |', '| SPECTER-011 | Implement PostgreSQL connection pool in Rust | EPIC 02 | P0 | READY |')
idx = idx.replace('| COMPLETED | 3 |', '| COMPLETED | 5 |')
idx = idx.replace('| READY | 1 |', '| READY | 2 |')
idx = idx.replace('| BACKLOG | 126 |', '| BACKLOG | 123 |')

with open('tasks/TASK_INDEX.md', 'w', encoding='utf-8') as f:
    f.write(idx)

# Update memory/EXECUTION_STATE.md
with open('memory/EXECUTION_STATE.md', 'r', encoding='utf-8') as f:
    es = f.read()

es = es.replace('- **COMPLETED Tasks**: 3 (`SPECTER-001`, `SPECTER-002`, `SPECTER-003`)', '- **COMPLETED Tasks**: 5 (`SPECTER-001`, `SPECTER-002`, `SPECTER-003`, `SPECTER-004`, `SPECTER-005`)')
es = es.replace('- **READY Tasks**: 1 (`SPECTER-004`)', '- **READY Tasks**: 2 (`SPECTER-006`, `SPECTER-011`)')
es = es.replace('- **Total Backlog Tasks**: 126', '- **Total Backlog Tasks**: 123')

with open('memory/EXECUTION_STATE.md', 'w', encoding='utf-8') as f:
    f.write(es)

print('Updated TASK_INDEX.md and EXECUTION_STATE.md')

