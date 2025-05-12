import os
import json
import random
from collections import defaultdict
import yaml
from copy import deepcopy
from collections import Counter

class OmniPromptFormatter:
    def __init__(self, prompt_path="prompt.txt", usernames_path="training_data/simulated_users/usernames.txt", seed=42):
        random.seed(seed)

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

        # Load training data
        self.fact_types = self.load_fact_types()
        self.training_data = self.load_training_data()
        self.write_training_file('all.jsonl')

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

    def generate_training_row(self, data, simulate_state=True, extra_chat=None):
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


        else:
            # Empty world state (not connected)
            players = [{"Username": "", "Health": "null", "Team": ""} for _ in range(8)]
            connection_status = "not_connected"
            map_choice = ""
            mode = ""

        
        chat = ""
        if extra_chat:
            chat = f"{self.usernames.pop()}: {extra_chat['q']}\n" + f"Omni: {extra_chat['a']}\n"
        chat += f"{self.usernames.pop()}: {data['q']}"

        instruction = self.fill_prompt(connection_status, map_choice, mode, players, chat)
        output = f"command: {data['c']}\nchat_response: {data['a']}"

        return {"instruction": instruction, "output": output}

    def assemble_inference_prompt(self, connection_status=None, map_name=None, mode=None, players=None, chat_log="", sim_in_game=False):
        """If sim_in_game=True, auto-generate a plausible in-game state."""
        if sim_in_game:
            connection_status = "in_game"
            map_name = random.choice(self.maps)
            mode = random.choice(self.modes)
            players = self.default_players(random.randint(2, 8))
        else:
            # Use provided or default empty state
            connection_status = connection_status or "not_connected"
            map_name = map_name or ""
            mode = mode or ""
            players = players or [{"Username": "", "Health": "null", "Team": ""} for _ in range(8)]

        return self.fill_prompt(connection_status, map_name, mode, players, chat_log)

    def default_players(self, num_players=3):
        """Return a default set of players with Omni always included but not as the first player."""
        if num_players > 8:
            num_players = 8

        base_names = ["AlphaRider", "NeoSniper", "CyberWolf", "GhostBlaze", "VoltCrush", "DarkViper", "SteelHunter"]
        random.shuffle(base_names)
        selected_names = base_names[:num_players - 1]  # Leave room for Omni

        teams = self.assign_teams_deathmatch(num_players)
        healths = [random.choice(self.possible_health) for _ in range(num_players)]

        # Insert Omni at a random position but not first
        omni_position = random.randint(1, num_players - 1)
        usernames = selected_names.copy()
        usernames.insert(omni_position, "Omni")

        players = []
        for i in range(num_players):
            players.append({
                "Username": usernames[i],
                "Health": healths[i],
                "Team": teams[i]
            })

        # Pad to 8 players
        while len(players) < 8:
            players.append({"Username": "", "Health": "null", "Team": ""})

        return players

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

    def load_fact_types(self):
        print("Reading in fact types ...")
        with open('training_data/fact_types.yaml', 'r') as f:
            data = yaml.safe_load(f)

        fact_types = {}
        data = data['fact_types']
        for fact_category in data.keys():
            for fact_type in data[fact_category].keys():
                fact_types[fact_type] = data[fact_category][fact_type]['question_formats']
                print(f"  Fact type: {fact_type} has {len(fact_types[fact_type])} question formats.")
        return fact_types

    def load_training_data(self):
        def format_fact_type_question(params, question):
            for param, param_value in params.items():
                if f'{{{param}}}' in question:
                    question = question.replace(f'{{{param}}}', param_value)
            return question
        
        def format_yaml_file(file, fact_types):
            all_qa = []
            
            data = yaml.safe_load(f)
            params = data['facts']['params'] if 'params' in data['facts'].keys() else {}
            entries = data['facts']['entries']
            command = params['command'] if 'command' in params else 'no_command'

            for fact_type, answers in entries.items():
                fact_type_questions = deepcopy(fact_types[fact_type])
                fact_type_questions = [format_fact_type_question(params, question) for question in fact_type_questions]
                
                for question in fact_type_questions:
                    for answer in answers:
                        all_qa.append(
                            {
                                'file': file,
                                'c': command,
                                'q': question,
                                'a': answer,
                                'ft': fact_type
                            }
                        )
            print(f"  {file} generated {len(all_qa)} datapoints!")
            return all_qa

        data = []

        for dirpath, _, filenames in os.walk('training_data'):
            for fname in filenames:
                full_path = os.path.join(dirpath, fname)

                if fname.endswith('.yaml') and fname != 'fact_types.yaml':
                    with open(full_path, 'r') as f:
                        print(f"Loading {full_path} ...")
                        data += (format_yaml_file(full_path, self.fact_types))

                elif fname.endswith('.jsonl'):
                    with open(full_path, 'r') as f:
                        lines = [json.loads(line) for line in f if line.strip()]
                        for line in lines:
                            data.append({
                                    'file': full_path,
                                    'c': 'no_command',
                                    'q': line['q'],
                                    'a': line['a'],
                                    'ft': 'refusals'
                                })

        print("===========================")
        print("Fact type distribution:")
        fact_type_counts = Counter(item['ft'] for item in data if 'ft' in item)
        for ft, count in fact_type_counts.most_common():
            print(f"  {ft}: {count}")

        return data

    def deranged_copy(self, lst):
        n = len(lst)
        if n < 2:
            raise ValueError("List must contain at least 2 elements for a derangement.")

        result = lst[:]
        for i in range(n - 1):
            j = random.randrange(i + 1, n)
            result[i], result[j] = result[j], result[i]

        # Final check for last element
        if result[-1] == lst[-1]:
            result[-1], result[-2] = result[-2], result[-1]

        return result

    def write_training_file(self, output_path):
        print("Writing training file ...")
        total = 0

        extra_chat_row = self.deranged_copy(self.training_data)

        with open(output_path, 'w', encoding='utf-8') as f:
            for i, record in enumerate(self.training_data):
                row = self.generate_training_row(record, simulate_state=(i % 2 != 0), extra_chat=extra_chat_row[i])
                if i % 2 != 0:
                    assert 'Username\\\": \\\"Omni' in json.dumps(row)
                f.write(json.dumps(row) + '\n')
                total += 1
        print(f"Wrote {total} training datapoints.")
        return total

# Example usage for training
if __name__ == "__main__":
    formatter = OmniPromptFormatter()



    # all_data = formatter.load_all_data()
    # total_rows = formatter.write_training_file(all_data, "all.jsonl")

    # print(f"Loaded prompt template ({len(formatter.prompt_template)} characters).")
    # for key, value in all_data.items():
    #     print(f"Loaded {len(value)} {key} JSON records")
    # print("=====================")
    # print(f"Loaded {total_rows} total JSONL records.")
