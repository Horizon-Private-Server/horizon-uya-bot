#!/bin/bash
set -e
set -o pipefail

export MODEL_PATH="./full_finetune_output"

python3 <<EOF
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("${MODEL_PATH}", device_map="cuda:0", torch_dtype=torch.bfloat16)
tokenizer = AutoTokenizer.from_pretrained("${MODEL_PATH}")

def ask(question):
    prompt = "[INST] <<SYS>>
You are Omni, an expert assistant for Ratchet & Clank: Up Your Arsenal multiplayer. You want to help players learn to play UYA and learn to play competitively. You are able to join games and play. You control another agent that can perform actions in game. You observe player chat and the current game state. You can chat with users and you can optionally join games and play with them. You only respond with:
- A command string for the game bot.
- A chat response to explain the action.

General output format is:
command: [chosen_command]
chat_response: [chat_response]

If no action is required, respond with:
command: no_command
chat_response: (empty string)

Valid commands:
[
    "join_game(game_name)",
    "freeze",
    "defend",
    "kill",
    "no_command" 
]

Never generate explanations beyond the chat_response line. Never output extra text. Never use emojis or hashtags.
<</SYS>>

[WORLD STATE]
{
    "connection_status": "in_game",
    "map": "Blackwater Docks",
    "mode": "Deathmatch",
    "players": {
        "Player1": {"Username": "NeoFurySniper1681", "Health": 46, "Team": "orange"},
        "Player2": {"Username": "Omni", "Health": 53, "Team": "aqua"},
        "Player3": {"Username": "DarkSteelMaster", "Health": 40, "Team": "red"},
        "Player4": {"Username": "", "Health": null, "Team": ""},
        "Player5": {"Username": "", "Health": null, "Team": ""},
        "Player6": {"Username": "", "Health": null, "Team": ""},
        "Player7": {"Username": "", "Health": null, "Team": ""},
        "Player8": {"Username": "", "Health": null, "Team": ""}
    }
}

[RECENT CHAT]
FourBolt: {question}
[/INST]"""
    prompt = prompt.replace("{question}", question)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=100)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    print(f"Q: {question}")
    print(f"A: {response}")
    print("="*50)

ask("What is the Minirocket Tube?")
ask("Is friendly fire enabled in UYA?")
ask("How do you upgrade the N60 Storm?")
EOF

