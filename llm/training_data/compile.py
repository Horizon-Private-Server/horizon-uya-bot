import os
import json
import random

def assign_teams_deathmatch(num_players):
    colors = ['blue', 'red', 'green', 'orange', 'yellow', 'purple', 'aqua', 'pink']
    num_colors = len(colors)

    assignments = []
    for i in range(num_players):
        assignments.append(random.choice(colors))

    random.shuffle(assignments)
    return assignments


def assign_teams(num_players):
    red_count = num_players // 2 + num_players % 2  # Red gets extra if odd
    blue_count = num_players - red_count
    teams = ['red'] * red_count + ['blue'] * blue_count
    random.shuffle(teams)
    return teams


def empty_format_no_command(prompt_template, usernames, data):
    filled_prompt = prompt_template
    filled_prompt = filled_prompt.replace("{connection_status}", "not_connected")
    filled_prompt = filled_prompt.replace("{map}", "")
    filled_prompt = filled_prompt.replace("{mode}", "")

    for i in range(1, 9):
        filled_prompt = filled_prompt.replace(f"{{p{i}_username}}", "")
        filled_prompt = filled_prompt.replace(f"{{p{i}_health}}", "null")
        filled_prompt = filled_prompt.replace(f"{{p{i}_team}}", "")

    chat = f"{usernames.pop()}: {data['q']}"
    filled_prompt = filled_prompt.replace("{chat_log}", chat)

    output = f"command: no_command\nchat_response: Omni: {data['a']}"
    this_row = {"instruction": filled_prompt, "output": output}
    return this_row

def simulated_state(prompt_template, usernames, data):
    maps = ['Bakisi Isles', 'Metropolis', 'Outpost X12', 'Korgon Outpost', 'Hoven Gorge', 'Blackwater Docks', 'Command Center', 'Marcadia Palace', 'Aquatos Sewers', 'Blackwater City']
    modes = ['Siege', 'CTF', 'Deathmatch']
    connection_statuses = ['in_game', 'staging']
    possible_health = [100, 93, 86, 80, 73, 66, 60, 53, 46, 40, 33, 26, 20, 13, 6, 0]

    num_players_possibilities = [2,3,4,5,6,7,8]

    mode = random.choice(modes)
    if mode == 'Siege':
        map = random.choice(['Bakisi Isles', 'Metropolis', 'Outpost X12', 'Korgon Outpost', 'Hoven Gorge', 'Blackwater City'])
    else:
        map = random.choice(maps)
    connection_status = random.choice(connection_statuses)
    num_players = random.choice(num_players_possibilities)

    if mode == 'Deathmatch':
        teams = assign_teams_deathmatch(num_players)
    else: # Siege/CTF
        teams = assign_teams(num_players)


    if connection_status == 'in_game':
        healths = [str(random.choice(possible_health)) for i in range(num_players)]
    else:
        healths = ["100"] * num_players

    usernames_selected = [usernames.pop() for i in range(num_players-1)]
    first_player = usernames_selected.pop()
    usernames_selected = usernames_selected + ['Omni']
    random.shuffle(usernames_selected)
    usernames_selected = [first_player] + usernames_selected

    filled_prompt = prompt_template
    filled_prompt = filled_prompt.replace("{connection_status}", connection_status)
    filled_prompt = filled_prompt.replace("{map}", map)
    filled_prompt = filled_prompt.replace("{mode}", mode)

    assert len(usernames_selected) == len(teams) and len(teams) == num_players and usernames_selected[0] != 'Omni' and 'Omni' in usernames_selected

    for i in range(1, 9):
        if i < num_players + 1:
            filled_prompt = filled_prompt.replace(f"{{p{i}_username}}", usernames_selected[i-1])
            filled_prompt = filled_prompt.replace(f"{{p{i}_health}}", healths[i-1])
            filled_prompt = filled_prompt.replace(f"{{p{i}_team}}", teams[i-1])
        else:
            filled_prompt = filled_prompt.replace(f"{{p{i}_username}}", "")
            filled_prompt = filled_prompt.replace(f"{{p{i}_health}}", "null")
            filled_prompt = filled_prompt.replace(f"{{p{i}_team}}", "")

    chat = f"{usernames.pop()}: {data['q']}"
    filled_prompt = filled_prompt.replace("{chat_log}", chat)

    output = f"command: no_command\nchat_response: Omni: {data['a']}"
    this_row = {"instruction": filled_prompt, "output": output}

    return this_row


if __name__ == '__main__':
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

    # # Read commands
    # with open("commands/join_game.jsonl", "r", encoding="utf-8") as f:
    #     prompt_template = f.read()

    total_rows = 0
    # Write 
    with open('../all.jsonl', 'w') as f:
        for i, atomic in enumerate(atomic_data):
            if i % 2 == 0:
                this_row = empty_format_no_command(prompt_template, usernames, atomic)
            else:
                this_row = simulated_state(prompt_template, usernames, atomic)
                #print(json.dumps(this_row, indent=4))
                assert 'Username\\\": \\\"Omni' in json.dumps(this_row)

            print("Instruction:")
            print(this_row['instruction'])
            print("Output:")
            print(this_row['output'])
            print()

            f.write(json.dumps(this_row) + '\n')
            total_rows += 1

    print(f"Loaded prompt template ({len(prompt_template)} characters).")
    print(f"Loaded {len(atomic_data)} JSONL records from atomic/ folder.")
    print(f"Loaded {total_rows} total JSONL records.")