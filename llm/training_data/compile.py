import os
import json
import random
random.seed(42)

# Read usernames from the file
with open("usernames.txt", "r", encoding="utf-8") as f:
    usernames = [line.strip() for line in f if line.strip()]

# Shuffle the list
random.shuffle(usernames)

# Step 1: Read the prompt template
with open("prompt.txt", "r", encoding="utf-8") as f:
    prompt_template = f.read()

# Step 2: Read all JSONL files in atomic/ recursively
atomic_data = []

for root, dirs, files in os.walk("atomic"):
    for file in files:
        if file.endswith(".jsonl"):
            filepath = os.path.join(root, file)
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            atomic_data.append(data)
                        except json.JSONDecodeError:
                            pass  # or raise if you want to catch bad lines

# Read commands
with open("commands/join_game.jsonl", "r", encoding="utf-8") as f:
    prompt_template = f.read()


def empty_format_no_command():
    filled_prompt = prompt_template
    filled_prompt = filled_prompt.replace("{connection_status}", "not_connected")
    filled_prompt = filled_prompt.replace("{map}", "")

    for i in range(1, 9):
        filled_prompt = filled_prompt.replace(f"{{p{i}_username}}", "")
        filled_prompt = filled_prompt.replace(f"{{p{i}_health}}", "null")

    instruction = filled_prompt
    input = f"{usernames.pop()}: {atomic['q']}"
    output = f"command: no_command\nchat_response: Omni: {atomic['a']}"
    this_row = {"instruction": instruction, "input": input, "output": output}
    return this_row


total_rows = 0
# Write 
with open('../all.jsonl', 'w') as f:
    for atomic in atomic_data:
        this_row = empty_format_no_command(atomic)
        f.write(json.dumps(this_row) + '\n')
        total_rows += 1

print(f"Loaded prompt template ({len(prompt_template)} characters).")
print(f"Loaded {len(atomic_data)} JSONL records from atomic/ folder.")
print(f"Loaded {total_rows} total JSONL records.")