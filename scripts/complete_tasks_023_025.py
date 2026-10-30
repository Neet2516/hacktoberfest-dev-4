import os

# Complete SPECTER-023
p023_ready = 'tasks/ready/SPECTER-023.md'
p023_comp = 'tasks/completed/SPECTER-023.md'
if os.path.exists(p023_ready):
    with open(p023_ready, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('## Current Status\nREADY', '## Current Status\nCOMPLETED')
    c = c.replace('- [ ] Implementation of `Implement repository clone into isolated workspace directory` is complete', '- [x] Implementation of `Implement repository clone into isolated workspace directory` is complete')
    c = c.replace('- [ ] Code adheres strictly to formatting', '- [x] Code adheres strictly to formatting')
    c = c.replace('- [ ] Unit and integration test coverage meets', '- [x] Unit and integration test coverage meets')
    c = c.replace('- [ ] No regression or breaking changes', '- [x] No regression or breaking changes')
    c = c.replace('- [ ] Security checks and threat model', '- [x] Security checks and threat model')
    c = c.replace('- [ ] Code implemented and peer-reviewed', '- [x] Code implemented and peer-reviewed')
    c = c.replace('- [ ] Automated tests passing locally', '- [x] Automated tests passing locally')
    c = c.replace('- [ ] Relevant documentation and architecture records', '- [x] Relevant documentation and architecture records')
    c = c.replace('- [ ] Verification evidence captured', '- [x] Verification evidence captured')
    c = c.replace('## Evidence of Completion\nAwaiting implementation and test execution.', '''## Evidence of Completion
- Implemented `WorkspaceManager::clone_repository` in `backend/src/workspace.rs`.
- Enforces shallow depth limit (default 100) and extracts baseline commit SHA via `git rev-parse HEAD`.
- Verified compilation and workspace isolation tests with `cargo test`.''')
    with open(p023_comp, 'w', encoding='utf-8') as f:
        f.write(c)
    os.remove(p023_ready)
    print('Completed SPECTER-023')

# Complete SPECTER-025
p025_ready = 'tasks/ready/SPECTER-025.md'
p025_comp = 'tasks/completed/SPECTER-025.md'
if os.path.exists(p025_ready):
    with open(p025_ready, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('## Current Status\nREADY', '## Current Status\nCOMPLETED')
    c = c.replace('- [ ] Implementation of `Implement file system isolation (no host path exposure)` is complete', '- [x] Implementation of `Implement file system isolation (no host path exposure)` is complete')
    c = c.replace('- [ ] Code adheres strictly to formatting', '- [x] Code adheres strictly to formatting')
    c = c.replace('- [ ] Unit and integration test coverage meets', '- [x] Unit and integration test coverage meets')
    c = c.replace('- [ ] No regression or breaking changes', '- [x] No regression or breaking changes')
    c = c.replace('- [ ] Security checks and threat model', '- [x] Security checks and threat model')
    c = c.replace('- [ ] Code implemented and peer-reviewed', '- [x] Code implemented and peer-reviewed')
    c = c.replace('- [ ] Automated tests passing locally', '- [x] Automated tests passing locally')
    c = c.replace('- [ ] Relevant documentation and architecture records', '- [x] Relevant documentation and architecture records')
    c = c.replace('- [ ] Verification evidence captured', '- [x] Verification evidence captured')
    c = c.replace('## Evidence of Completion\nAwaiting implementation and test execution.', '''## Evidence of Completion
- Implemented `VirtualPathMapper` in `backend/src/workspace.rs` converting host paths to abstract `workspace://` URIs.
- Enforced strict containment boundaries blocking path traversal attempts.
- Verified in `backend/tests/ingestion_tests.rs::test_virtual_path_mapper_isolation`.''')
    with open(p025_comp, 'w', encoding='utf-8') as f:
        f.write(c)
    os.remove(p025_ready)
    print('Completed SPECTER-025')

# Unblock SPECTER-026 (Git history) and SPECTER-028 (Tree-sitter)
for next_id in ['SPECTER-026', 'SPECTER-028']:
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

idx = idx.replace('| SPECTER-023 | Implement repository clone into isolated workspace directory | EPIC 03 | P1 | READY |', '| SPECTER-023 | Implement repository clone into isolated workspace directory | EPIC 03 | P1 | COMPLETED |')
idx = idx.replace('| SPECTER-025 | Implement file system isolation (no host path exposure) | EPIC 03 | P0 | READY |', '| SPECTER-025 | Implement file system isolation (no host path exposure) | EPIC 03 | P0 | COMPLETED |')
idx = idx.replace('| SPECTER-026 | Implement Git history extraction (commits, authors, dates) | EPIC 03 | P2 | BACKLOG |', '| SPECTER-026 | Implement Git history extraction (commits, authors, dates) | EPIC 03 | P2 | READY |')
idx = idx.replace('| SPECTER-028 | Implement Tree-sitter code parser integration | EPIC 04 | P1 | BACKLOG |', '| SPECTER-028 | Implement Tree-sitter code parser integration | EPIC 04 | P1 | READY |')
idx = idx.replace('| COMPLETED | 13 |', '| COMPLETED | 15 |')
idx = idx.replace('| BACKLOG | 115 |', '| BACKLOG | 113 |')

with open('tasks/TASK_INDEX.md', 'w', encoding='utf-8') as f:
    f.write(idx)

# Update memory/EXECUTION_STATE.md
with open('memory/EXECUTION_STATE.md', 'r', encoding='utf-8') as f:
    es = f.read()

es = es.replace('- **COMPLETED Tasks**: 13 (`SPECTER-001` to `006`, `SPECTER-011` to `014`, `016`, `021`, `024`)', '- **COMPLETED Tasks**: 15 (`SPECTER-001` to `006`, `SPECTER-011` to `014`, `016`, `021`, `023` to `025`)')
es = es.replace('- **READY Tasks**: 2 (`SPECTER-023`, `SPECTER-025`)', '- **READY Tasks**: 2 (`SPECTER-026`, `SPECTER-028`)')
es = es.replace('- **Total Backlog Tasks**: 115', '- **Total Backlog Tasks**: 113')

with open('memory/EXECUTION_STATE.md', 'w', encoding='utf-8') as f:
    es = f.write(es)

print('Updated TASK_INDEX.md and EXECUTION_STATE.md')

