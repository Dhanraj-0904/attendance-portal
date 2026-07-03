import os
import json

log_path = r"C:\Users\dhanr\.gemini\antigravity\brain\a215ce0e-7f7f-4126-9dc8-7eb782cefd13\.system_generated\logs\transcript_full.jsonl"

if os.path.exists(log_path):
    print("Searching transcript logs...")
    with open(log_path, 'r', encoding='utf-8') as f:
        count = 0
        for idx, line in enumerate(f):
            if '"type":"USER_INPUT"' in line:
                data = json.loads(line)
                content = data.get("content", "")
                print(f"Step {data.get('step_index')}: {content[:150]}")
                count += 1
                if count > 40:
                    break
else:
    print("Log path not found!")
