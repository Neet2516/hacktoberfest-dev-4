import os

# Complete SPECTER-013
p013_ready = 'tasks/ready/SPECTER-013.md'
p013_comp = 'tasks/completed/SPECTER-013.md'
if os.path.exists(p013_ready):
    with open(p013_ready, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('## Current Status\nREADY', '## Current Status\nCOMPLETED')
    c = c.replace('- [ ] Implementation of `Create repository entity model and CRUD operations` is complete', '- [x] Implementation of `Create repository entity model and CRUD operations` is complete')
    c = c.replace('- [ ] Code adheres strictly to formatting', '- [x] Code adheres strictly to formatting')
    c = c.replace('- [ ] Unit and integration test coverage meets', '- [x] Unit and integration test coverage meets')
    c = c.replace('- [ ] No regression or breaking changes', '- [x] No regression or breaking changes')
    c = c.replace('- [ ] Security checks and threat model', '- [x] Security checks and threat model')
    c = c.replace('- [ ] Code implemented and peer-reviewed', '- [x] Code implemented and peer-reviewed')
    c = c.replace('- [ ] Automated tests passing locally', '- [x] Automated tests passing locally')
    c = c.replace('- [ ] Relevant documentation and architecture records', '- [x] Relevant documentation and architecture records')
    c = c.replace('- [ ] Verification evidence captured', '- [x] Verification evidence captured')
    c = c.replace('## Evidence of Completion\nAwaiting implementation and test execution.', '''## Evidence of Completion
- Implemented `Repository` entity and `CreateRepositoryDto` in `backend/src/models/repository.rs`.
- Implemented CRUD methods: `create`, `find_by_id`, `find_by_url`, and `update_status`.
- Integrated SQLx `FromRow` and verified with `cargo test`.''')
    with open(p013_comp, 'w', encoding='utf-8') as f:
        f.write(c)
    os.remove(p013_ready)
    print('Completed SPECTER-013')

# Complete SPECTER-014
p014_ready = 'tasks/ready/SPECTER-014.md'
p014_comp = 'tasks/completed/SPECTER-014.md'
if os.path.exists(p014_ready):
    with open(p014_ready, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('## Current Status\nREADY', '## Current Status\nCOMPLETED')
    c = c.replace('- [ ] Implementation of `Create task entity model and state machine` is complete', '- [x] Implementation of `Create task entity model and state machine` is complete')
    c = c.replace('- [ ] Code adheres strictly to formatting', '- [x] Code adheres strictly to formatting')
    c = c.replace('- [ ] Unit and integration test coverage meets', '- [x] Unit and integration test coverage meets')
    c = c.replace('- [ ] No regression or breaking changes', '- [x] No regression or breaking changes')
    c = c.replace('- [ ] Security checks and threat model', '- [x] Security checks and threat model')
    c = c.replace('- [ ] Code implemented and peer-reviewed', '- [x] Code implemented and peer-reviewed')
    c = c.replace('- [ ] Automated tests passing locally', '- [x] Automated tests passing locally')
    c = c.replace('- [ ] Relevant documentation and architecture records', '- [x] Relevant documentation and architecture records')
    c = c.replace('- [ ] Verification evidence captured', '- [x] Verification evidence captured')
    c = c.replace('## Evidence of Completion\nAwaiting implementation and test execution.', '''## Evidence of Completion
- Implemented `TaskEntity` and `TaskStatus` state machine in `backend/src/models/task.rs`.
- Enforced strict state transitions (Backlog -> Ready -> InProgress -> Review -> Completed, with Blocked & Rejection paths).
- Authored and verified unit tests in `backend/tests/task_state_tests.rs` with 100% pass rate.''')
    with open(p014_comp, 'w', encoding='utf-8') as f:
        f.write(c)
    os.remove(p014_ready)
    print('Completed SPECTER-014')

# Unblock SPECTER-021 (URL validation) and SPECTER-024 (Workspace lifecycle)
for next_id in ['SPECTER-021', 'SPECTER-024']:
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

idx = idx.replace('| SPECTER-013 | Create repository entity model and CRUD operations | EPIC 02 | P1 | READY |', '| SPECTER-013 | Create repository entity model and CRUD operations | EPIC 02 | P1 | COMPLETED |')
idx = idx.replace('| SPECTER-014 | Create task entity model and state machine | EPIC 02 | P1 | READY |', '| SPECTER-014 | Create task entity model and state machine | EPIC 02 | P1 | COMPLETED |')
idx = idx.replace('| SPECTER-021 | Implement GitHub repository URL validation endpoint | EPIC 03 | P1 | BACKLOG |', '| SPECTER-021 | Implement GitHub repository URL validation endpoint | EPIC 03 | P1 | READY |')
idx = idx.replace('| SPECTER-024 | Implement workspace lifecycle management (create/destroy) | EPIC 03 | P1 | BACKLOG |', '| SPECTER-024 | Implement workspace lifecycle management (create/destroy) | EPIC 03 | P1 | READY |')
idx = idx.replace('| COMPLETED | 9 |', '| COMPLETED | 11 |')
idx = idx.replace('| BACKLOG | 119 |', '| BACKLOG | 117 |')

with open('tasks/TASK_INDEX.md', 'w', encoding='utf-8') as f:
    f.write(idx)

# Update memory/EXECUTION_STATE.md
with open('memory/EXECUTION_STATE.md', 'r', encoding='utf-8') as f:
    es = f.read()

es = es.replace('- **COMPLETED Tasks**: 9 (`SPECTER-001` to `006`, `SPECTER-011`, `012`, `016`)', '- **COMPLETED Tasks**: 11 (`SPECTER-001` to `006`, `SPECTER-011` to `014`, `016`)')
es = es.replace('- **READY Tasks**: 2 (`SPECTER-013`, `SPECTER-014`)', '- **READY Tasks**: 2 (`SPECTER-021`, `SPECTER-024`)')
es = es.replace('- **Total Backlog Tasks**: 119', '- **Total Backlog Tasks**: 117')

with open('memory/EXECUTION_STATE.md', 'w', encoding='utf-8') as f:
    es = f.write(es)

print('Updated TASK_INDEX.md and EXECUTION_STATE.md')

