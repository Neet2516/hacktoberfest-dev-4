import json
import os
from datetime import datetime

transcript_path = 'logs/transcript_full.jsonl'
output_log_path = 'logs/SESSION_EXECUTION_LOG.md'

steps = []
if os.path.exists(transcript_path):
    with open(transcript_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    steps.append(json.loads(line))
                except Exception:
                    pass

log_lines = []
log_lines.append("# SPECTER — Session Execution & Event Audit Log")
log_lines.append("")
log_lines.append(f"**Generated At**: {datetime.utcnow().isoformat()}Z")
log_lines.append(f"**Session ID**: `d4477168-580b-4e54-aa12-53a5340ec19b`")
log_lines.append(f"**Total Trace Events Captured**: {len(steps)}")
log_lines.append(f"**Raw Transcripts Stored**: [`logs/transcript.jsonl`](transcript.jsonl) | [`logs/transcript_full.jsonl`](transcript_full.jsonl)")
log_lines.append("")
log_lines.append("---")
log_lines.append("")
log_lines.append("## 1. Session Trajectory Summary")
log_lines.append("")
log_lines.append("| Step | Timestamp | Source | Type | Action / Tool / Event | Status |")
log_lines.append("|---|---|---|---|---|---|")

for s in steps:
    step_idx = s.get('step_index', '-')
    created_at = s.get('created_at', '')
    source = s.get('source', '')
    step_type = s.get('type', '')
    status = s.get('status', '')
    
    # Extract action summary
    action = '-'
    tool_calls = s.get('tool_calls', [])
    if tool_calls:
        tool_names = [tc.get('name') or tc.get('tool_name') or 'tool' for tc in tool_calls]
        action = f"Call: {', '.join(tool_names)}"
    elif step_type == 'USER_INPUT':
        action = "User Request Prompt"
    elif step_type == 'PLANNER_RESPONSE':
        action = "Agent Response / Planning"
    elif step_type == 'TASK_COMPLETION':
        action = "Subagent / Task Completed"
    
    # Truncate timestamp for brevity
    time_str = created_at.replace('T', ' ')[:19] if created_at else '-'
    log_lines.append(f"| {step_idx} | {time_str} | `{source}` | `{step_type}` | {action} | `{status}` |")

log_lines.append("")
log_lines.append("---")
log_lines.append("")
log_lines.append("## 2. Chronological Event Details")
log_lines.append("")

for s in steps:
    step_idx = s.get('step_index', '-')
    created_at = s.get('created_at', '')
    source = s.get('source', '')
    step_type = s.get('type', '')
    status = s.get('status', '')
    content = s.get('content', '')
    tool_calls = s.get('tool_calls', [])
    
    log_lines.append(f"### Step {step_idx} — `{source}` | `{step_type}` ({created_at})")
    log_lines.append(f"- **Status**: `{status}`")
    
    if tool_calls:
        log_lines.append("- **Tool Invocations**:")
        for tc in tool_calls:
            t_name = tc.get('name') or tc.get('tool_name') or 'unknown_tool'
            t_args = tc.get('arguments') or tc.get('args') or {}
            # abbreviate large string args
            args_summary = {}
            for k, v in t_args.items():
                if isinstance(v, str) and len(v) > 120:
                    args_summary[k] = v[:120] + "... [truncated]"
                else:
                    args_summary[k] = v
            log_lines.append(f"  - `{t_name}`: `{json.dumps(args_summary)}`")
            
    if content:
        # Include snippet of content
        content_snippet = content.strip()
        if len(content_snippet) > 500:
            content_snippet = content_snippet[:500] + "\n... [Remaining content in raw transcript]"
        log_lines.append("")
        log_lines.append("```text")
        log_lines.append(content_snippet)
        log_lines.append("```")
        
    log_lines.append("")
    log_lines.append("---")
    log_lines.append("")

with open(output_log_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines) + '\n')

print(f"Parsed {len(steps)} events into {output_log_path}")

