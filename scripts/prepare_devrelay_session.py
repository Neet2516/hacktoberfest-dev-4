import json
import re

def sanitize(text):
    if not isinstance(text, str):
        text = str(text)
    # Scrub common tokens
    text = re.sub(r'ghp_[a-zA-Z0-9]{20,}', '[REDACTED_GH_TOKEN]', text)
    text = re.sub(r'sk-[a-zA-Z0-9]{20,}', '[REDACTED_API_KEY]', text)
    text = re.sub(r'dev_[a-zA-Z0-9]{20,}', '[REDACTED_DEV_KEY]', text)
    # Scrub local home path
    text = text.replace(r'C:\Users\ASUS', '/home/user')
    text = text.replace(r'c:\Users\ASUS', '/home/user')
    return text

# Load transcript
messages = []
with open('logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except Exception:
            continue
        
        src = entry.get('source', '')
        stype = entry.get('type', '')
        content_text = entry.get('content', '')
        tool_calls = entry.get('tool_calls', [])
        
        # User message
        if stype == 'USER_INPUT' or src == 'USER_EXPLICIT':
            if content_text:
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": sanitize(content_text[:3000])}
                    ]
                })
        elif stype in ['PLANNER_RESPONSE', 'GENERIC'] or src == 'MODEL':
            content_blocks = []
            if content_text:
                # Add text block if substantive
                clean_text = sanitize(content_text)
                if len(clean_text) > 3000:
                    clean_text = clean_text[:3000] + "\n... [truncated for transcript view]"
                content_blocks.append({"type": "text", "text": clean_text})
            
            for tc in tool_calls:
                t_name = tc.get('name') or tc.get('tool_name') or 'run_command'
                t_args = tc.get('arguments') or tc.get('args') or {}
                # abbreviate input
                input_str = sanitize(json.dumps(t_args))
                if len(input_str) > 500:
                    input_str = input_str[:500] + "... [truncated]"
                content_blocks.append({
                    "type": "tool_call",
                    "name": t_name,
                    "input": input_str,
                    "output": "Executed successfully."
                })
            
            if content_blocks:
                messages.append({
                    "role": "assistant",
                    "model": "gemini-3.8-flash",
                    "content": content_blocks
                })

# Merge consecutive messages with the same role
merged_messages = []
for msg in messages:
    if merged_messages and merged_messages[-1]['role'] == msg['role']:
        merged_messages[-1]['content'].extend(msg['content'])
    else:
        merged_messages.append(msg)

curated_data = {
    "messages": merged_messages,
    "metadata": {
        "tool_name": "gemini_cli",
        "session_id": "d4477168-580b-4e54-aa12-53a5340ec19b",
        "project": "SPECTER — The Ghost Maintainer",
        "total_messages": len(merged_messages),
        "milestone": "Phase 1: Architecture, Agent Governance & Implementation Task Backlog"
    }
}

output_payload = {
    "title": "SPECTER: Autonomous Multi-Agent Architecture & Governance Setup",
    "tool_name": "gemini_cli",
    "curated_data": curated_data
}

with open('logs/devrelay_session_payload.json', 'w', encoding='utf-8') as f:
    json.dump(output_payload, f, indent=2)

print(f"Generated normalized DevRelay session payload with {len(merged_messages)} merged messages.")
