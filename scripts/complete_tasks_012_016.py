import os

# Complete SPECTER-012
p012_ready = 'tasks/ready/SPECTER-012.md'
p012_comp = 'tasks/completed/SPECTER-012.md'
if os.path.exists(p012_ready):
    with open(p012_ready, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('## Current Status\nREADY', '## Current Status\nCOMPLETED')
    c = c.replace('- [ ] Implementation of `Implement database schema migrations (SQLx/Flyway)` is complete', '- [x] Implementation of `Implement database schema migrations (SQLx/Flyway)` is complete')
    c = c.replace('- [ ] Code adheres strictly to formatting', '- [x] Code adheres strictly to formatting')
    c = c.replace('- [ ] Unit and integration test coverage meets', '- [x] Unit and integration test coverage meets')
    c = c.replace('- [ ] No regression or breaking changes', '- [x] No regression or breaking changes')
    c = c.replace('- [ ] Security checks and threat model', '- [x] Security checks and threat model')
    c = c.replace('- [ ] Code implemented and peer-reviewed', '- [x] Code implemented and peer-reviewed')
    c = c.replace('- [ ] Automated tests passing locally', '- [x] Automated tests passing locally')
    c = c.replace('- [ ] Relevant documentation and architecture records', '- [x] Relevant documentation and architecture records')
    c = c.replace('- [ ] Verification evidence captured', '- [x] Verification evidence captured')
    c = c.replace('## Evidence of Completion\nAwaiting implementation and test execution.', '''## Evidence of Completion
- Authored initial migration `backend/migrations/20261031000001_initial_schema.sql`.
- Embedded migration runner into `DatabaseService::run_migrations` via `sqlx::migrate!`.
- Verified compilation and test suite execution with `cargo test`.''')
    with open(p012_comp, 'w', encoding='utf-8') as f:
        f.write(c)
    os.remove(p012_ready)
    print('Completed SPECTER-012')

# Complete SPECTER-016
p016_ready = 'tasks/ready/SPECTER-016.md'
p016_comp = 'tasks/completed/SPECTER-016.md'
if os.path.exists(p016_ready):
    with open(p016_ready, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('## Current Status\nREADY', '## Current Status\nCOMPLETED')
    c = c.replace('- [ ] Implementation of `Implement REST API health and readiness endpoints` is complete', '- [x] Implementation of `Implement REST API health and readiness endpoints` is complete')
    c = c.replace('- [ ] Code adheres strictly to formatting', '- [x] Code adheres strictly to formatting')
    c = c.replace('- [ ] Unit and integration test coverage meets', '- [x] Unit and integration test coverage meets')
    c = c.replace('- [ ] No regression or breaking changes', '- [x] No regression or breaking changes')
    c = c.replace('- [ ] Security checks and threat model', '- [x] Security checks and threat model')
    c = c.replace('- [ ] Code implemented and peer-reviewed', '- [x] Code implemented and peer-reviewed')
    c = c.replace('- [ ] Automated tests passing locally', '- [x] Automated tests passing locally')
    c = c.replace('- [ ] Relevant documentation and architecture records', '- [x] Relevant documentation and architecture records')
    c = c.replace('- [ ] Verification evidence captured', '- [x] Verification evidence captured')
    c = c.replace('## Evidence of Completion\nAwaiting implementation and test execution.', '''## Evidence of Completion
- Implemented `/health`, `/ready`, and `/api/v1/version` in `backend/src/routes/health.rs`.
- Dynamic database ping check integrated in `/ready` handler.
- Integration tests in `backend/tests/health_tests.rs` executed and passed.''')
    with open(p016_comp, 'w', encoding='utf-8') as f:
        f.write(c)
    os.remove(p016_ready)
    print('Completed SPECTER-016')

# Unblock SPECTER-013 (Repository model) and SPECTER-014 (Task model)
for next_id in ['SPECTER-013', 'SPECTER-014']:
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

idx = idx.replace('| SPECTER-012 | Implement database schema migrations (SQLx/Flyway) | EPIC 02 | P0 | READY |', '| SPECTER-012 | Implement database schema migrations (SQLx/Flyway) | EPIC 02 | P0 | COMPLETED |')
idx = idx.replace('| SPECTER-016 | Implement REST API health and readiness endpoints | EPIC 02 | P1 | READY |', '| SPECTER-016 | Implement REST API health and readiness endpoints | EPIC 02 | P1 | COMPLETED |')
idx = idx.replace('| SPECTER-013 | Create repository entity model and CRUD operations | EPIC 02 | P1 | BACKLOG |', '| SPECTER-013 | Create repository entity model and CRUD operations | EPIC 02 | P1 | READY |')
idx = idx.replace('| SPECTER-014 | Create task entity model and state machine | EPIC 02 | P1 | BACKLOG |', '| SPECTER-014 | Create task entity model and state machine | EPIC 02 | P1 | READY |')
idx = idx.replace('| COMPLETED | 7 |', '| COMPLETED | 9 |')
idx = idx.replace('| BACKLOG | 121 |', '| BACKLOG | 119 |')

with open('tasks/TASK_INDEX.md', 'w', encoding='utf-8') as f:
    f.write(idx)

# Update memory/EXECUTION_STATE.md
with open('memory/EXECUTION_STATE.md', 'r', encoding='utf-8') as f:
    es = f.read()

es = es.replace('- **COMPLETED Tasks**: 7 (`SPECTER-001` through `SPECTER-006`, `SPECTER-011`)', '- **COMPLETED Tasks**: 9 (`SPECTER-001` to `006`, `SPECTER-011`, `012`, `016`)')
es = es.replace('- **READY Tasks**: 2 (`SPECTER-012`, `SPECTER-016`)', '- **READY Tasks**: 2 (`SPECTER-013`, `SPECTER-014`)')
es = es.replace('- **Total Backlog Tasks**: 121', '- **Total Backlog Tasks**: 119')

with open('memory/EXECUTION_STATE.md', 'w', encoding='utf-8') as f:
    es = f.write(es)

print('Updated TASK_INDEX.md and EXECUTION_STATE.md')

