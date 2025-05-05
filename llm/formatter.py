import os
import json
import random
from collections import defaultdict

class OmniPromptFormatter:
    def __init__(self, prompt_path, usernames_path=None):
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

        self.usernames = []
        if usernames_path:
            with open(usernames_path, "r", encoding="utf-8") as f:
                self.usernames = [line.strip() for line in f if line.strip()]
            random.shuffle(self.usernames)

        self.maps = ['Bakisi Isles', 'Metropolis', 'Outpost X12', 'Korgon Outpost', 'Hoven Gorge', 'Blackwater City'
                     'Blackwater Docks', 'Command Center', 'Marcadia Palace', 'Aquatos Sewers']
        self.modes = ['Siege', 'CTF', 'Deathmatch']
        self.connection_statuses = ['in_game', 'staging']
        self.possible_health = [100, 93, 86, 80, 73, 66, 60, 53, 46, 40, 33, 26, 20, 13, 6, 0]

    def fill_prompt(self, connection_status, map_name, mode, players, chat_log):
        filled = self.prompt_template
        filled = filled.replace("{connection_status}", connection_status)
        filled = filled.replace("{map}", map_name)
        filled = filled.replace("{mode}", mode)

        for i in range(1, 9):
            if i <= len(players):
                player = players[i - 1]
                filled = filled.replace(f"{{p{i}_username}}", player.get("Username", ""))
                filled = filled.replace(f"{{p{i}_health}}", str(player.get("Health", "null")))
                filled = filled.replace(f"{{p{i}_team}}", player.get("Team", ""))
            else:
                filled = filled.replace(f"{{p{i}_username}}", "")
                filled = filled.replace(f"{{p{i}_health}}", "null")
                filled = filled.replace(f"{{p{i}_team}}", "")

        filled = filled.replace("{chat_log}", chat_log)
        return filled

    def assign_teams(self, num_players):
        red_count = num_players // 2 + num_players % 2
        blue_count = num_players - red_count
        teams = ['red'] * red_count + ['blue'] * blue_count
        random.shuffle(teams)
        return teams

    def assign_teams_deathmatch(self, num_players):
        colors = ['blue', 'red', 'green', 'orange', 'yellow', 'purple', 'aqua', 'pink']
        assignments = [random.choice(colors) for _ in range(num_players)]
        random.shuffle(assignments)
        return assignments

    def generate_training_row(self, data, simulate_state=True):
        if simulate_state:
            num_players = random.choice([2, 3, 4, 5, 6, 7, 8])
            mode = random.choice(self.modes)
            map_choice = random.choice(self.maps if mode != 'Siege' else self.maps[:6])
            connection_status = random.choice(self.connection_statuses)

            if mode == 'Deathmatch':
                teams = self.assign_teams_deathmatch(num_players)
            else:
                teams = self.assign_teams(num_players)

            if connection_status == 'in_game':
                healths = [str(random.choice(self.possible_health)) for _ in range(num_players)]
            else:
                healths = ["100"] * num_players

            usernames_selected = [self.usernames.pop() for _ in range(num_players - 1)]
            first_player = usernames_selected.pop()
            usernames_selected.append('Omni')
            random.shuffle(usernames_selected)
            usernames_selected = [first_player] + usernames_selected

            players = []
            for username, health, team in zip(usernames_selected, healths, teams):
                players.append({
                    "Username": username,
                    "Health": health,
                    "Team": team
                })

            chat = f"{self.usernames.pop()}: {data['q']}"

        else:
            # Empty world state (not connected)
            players = [{"Username": "", "Health": "null", "Team": ""} for _ in range(8)]
            connection_status = "not_connected"
            map_choice = ""
            mode = ""
            chat = f"{self.usernames.pop()}: {data['q']}"

        instruction = self.fill_prompt(connection_status, map_choice, mode, players, chat)
        print(instruction)
        output = f"command: no_command\nchat_response: Omni: {data['a']}"

        return {"instruction": instruction, "output": output}

    def assemble_inference_prompt(self, connection_status, map_name, mode, players, chat_log):
        return self.fill_prompt(connection_status, map_name, mode, players, chat_log)

    def read_jsonl(self, filepath):
        all_data = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        all_data.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return all_data

    def load_all_data(self):
        all_data = defaultdict(list)
        for root, dirs, files in os.walk("training_data/atomic"):
            for file in files:
                if file.endswith(".jsonl"):
                    all_data['atomic'] += self.read_jsonl(os.path.join(root, file))
        all_data['command_explanations'] = self.read_jsonl('training_data/special/command_explanations.jsonl')
        all_data['negative_facts'] = self.read_jsonl('training_data/special/negative_facts.jsonl')
        all_data['refusals'] = self.read_jsonl('training_data/special/refusals.jsonl')
        return all_data

    def write_training_file(self, all_data, output_path):
        total = 0
        with open(output_path, 'w', encoding='utf-8') as f:
            for category, records in all_data.items():
                for i, record in enumerate(records):
                    row = self.generate_training_row(record, simulate_state=(i % 2 != 0))
                    if i % 2 != 0:
                        assert 'Username\\\": \\\"Omni' in json.dumps(row)
                    f.write(json.dumps(row) + '\n')
                    total += 1
        return total

# Example usage for training
if __name__ == "__main__":
    random.seed(42)
    formatter = OmniPromptFormatter("prompt.txt", "training_data/usernames.txt")
    all_data = formatter.load_all_data()
    total_rows = formatter.write_training_file(all_data, "all.jsonl")

    print(f"Loaded prompt template ({len(formatter.prompt_template)} characters).")
    for key, value in all_data.items():
        print(f"Loaded {len(value)} {key} JSON records")
    print("=====================")
    print(f"Loaded {total_rows} total JSONL records.")
