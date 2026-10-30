import os

# Complete SPECTER-021
p021_ready = 'tasks/ready/SPECTER-021.md'
p021_comp = 'tasks/completed/SPECTER-021.md'
if os.path.exists(p021_ready):
    with open(p021_ready, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('## Current Status\nREADY', '## Current Status\nCOMPLETED')
    c = c.replace('- [ ] Implementation of `Implement GitHub repository URL validation endpoint` is complete', '- [x] Implementation of `Implement GitHub repository URL validation endpoint` is complete')
    c = c.replace('- [ ] Code adheres strictly to formatting', '- [x] Code adheres strictly to formatting')
    c = c.replace('- [ ] Unit and integration test coverage meets', '- [x] Unit and integration test coverage meets')
    c = c.replace('- [ ] No regression or breaking changes', '- [x] No regression or breaking changes')
    c = c.replace('- [ ] Security checks and threat model', '- [x] Security checks and threat model')
    c = c.replace('- [ ] Code implemented and peer-reviewed', '- [x] Code implemented and peer-reviewed')
    c = c.replace('- [ ] Automated tests passing locally', '- [x] Automated tests passing locally')
    c = c.replace('- [ ] Relevant documentation and architecture records', '- [x] Relevant documentation and architecture records')
    c = c.replace('- [ ] Verification evidence captured', '- [x] Verification evidence captured')
    c = c.replace('## Evidence of Completion\nAwaiting implementation and test execution.', '''## Evidence of Completion
- Implemented `POST /api/v1/repos/validate` endpoint in `backend/src/routes/ingestion.rs`.
- Enforced strict SSRF defenses (blocking localhost, private IPs) and canonical GitHub URL regex.
- Integration tests in `backend/tests/ingestion_tests.rs` executed and passed with 100% success.''')
    with open(p021_comp, 'w', encoding='utf-8') as f:
        f.write(c)
    os.remove(p021_ready)
    print('Completed SPECTER-021')

# Complete SPECTER-024
p024_ready = 'tasks/ready/SPECTER-024.md'
p024_comp = 'tasks/completed/SPECTER-024.md'
if os.path.exists(p024_ready):
    with open(p024_ready, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('## Current Status\nREADY', '## Current Status\nCOMPLETED')
    c = c.replace('- [ ] Implementation of `Implement workspace lifecycle management (create/destroy)` is complete', '- [x] Implementation of `Implement workspace lifecycle management (create/destroy)` is complete')
    c = c.replace('- [ ] Code adheres strictly to formatting', '- [x] Code adheres strictly to formatting')
    c = c.replace('- [ ] Unit and integration test coverage meets', '- [x] Unit and integration test coverage meets')
    c = c.replace('- [ ] No regression or breaking changes', '- [x] No regression or breaking changes')
    c = c.replace('- [ ] Security checks and threat model', '- [x] Security checks and threat model')
    c = c.replace('- [ ] Code implemented and peer-reviewed', '- [x] Code implemented and peer-reviewed')
    c = c.replace('- [ ] Automated tests passing locally', '- [x] Automated tests passing locally')
    c = c.replace('- [ ] Relevant documentation and architecture records', '- [x] Relevant documentation and architecture records')
    c = c.replace('- [ ] Verification evidence captured', '- [x] Verification evidence captured')
    c = c.replace('## Evidence of Completion\nAwaiting implementation and test execution.', '''## Evidence of Completion
- Implemented `WorkspaceManager` in `backend/src/workspace.rs` with containment boundaries.
- Managed ephemeral creation and secure destruction of isolated workspaces.
- Lifecycle tested and verified in `backend/tests/ingestion_tests.rs`.''')
    with open(p024_comp, 'w', encoding='utf-8') as f:
        f.write(c)
    os.remove(p024_ready)
    print('Completed SPECTER-024')

# Unblock SPECTER-023 (Clone) and SPECTER-025 (Filesystem isolation)
for next_id in ['SPECTER-023', 'SPECTER-025']:
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

idx = idx.replace('| SPECTER-021 | Implement GitHub repository URL validation endpoint | EPIC 03 | P1 | READY |', '| SPECTER-021 | Implement GitHub repository URL validation endpoint | EPIC 03 | P1 | COMPLETED |')
idx = idx.replace('| SPECTER-024 | Implement workspace lifecycle management (create/destroy) | EPIC 03 | P1 | READY |', '| SPECTER-024 | Implement workspace lifecycle management (create/destroy) | EPIC 03 | P1 | COMPLETED |')
idx = idx.replace('| SPECTER-023 | Implement repository clone into isolated workspace directory | EPIC 03 | P1 | BACKLOG |', '| SPECTER-023 | Implement repository clone into isolated workspace directory | EPIC 03 | P1 | READY |')
idx = idx.replace('| SPECTER-025 | Implement file system isolation (no host path exposure) | EPIC 03 | P0 | BACKLOG |', '| SPECTER-025 | Implement file system isolation (no host path exposure) | EPIC 03 | P0 | READY |')
idx = idx.replace('| COMPLETED | 11 |', '| COMPLETED | 13 |')
idx = idx.replace('| BACKLOG | 117 |', '| BACKLOG | 115 |')

with open('tasks/TASK_INDEX.md', 'w', encoding='utf-8') as f:
    f.write(idx)

# Update memory/EXECUTION_STATE.md
with open('memory/EXECUTION_STATE.md', 'r', encoding='utf-8') as f:
    es = f.read()

es = es.replace('- **COMPLETED Tasks**: 11 (`SPECTER-001` to `006`, `SPECTER-011` to `014`, `016`)', '- **COMPLETED Tasks**: 13 (`SPECTER-001` to `006`, `SPECTER-011` to `014`, `016`, `021`, `024`)')
es = es.replace('- **READY Tasks**: 2 (`SPECTER-021`, `SPECTER-024`)', '- **READY Tasks**: 2 (`SPECTER-023`, `SPECTER-025`)')
es = es.replace('- **Total Backlog Tasks**: 117', '- **Total Backlog Tasks**: 115')

with open('memory/EXECUTION_STATE.md', 'w', encoding='utf-8') as f:
    es = f.write(es)

print('Updated TASK_INDEX.md and EXECUTION_STATE.md')

