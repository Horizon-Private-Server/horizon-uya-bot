#!/bin/bash
set -e
set -o pipefail

export MODEL_PATH="./full_finetune_output"

python3 <<EOF
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from formatter import OmniPromptFormatter  # Your class is in formatter.py

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained("${MODEL_PATH}", device_map="cuda:0", torch_dtype=torch.bfloat16)
tokenizer = AutoTokenizer.from_pretrained("${MODEL_PATH}")

# Initialize the formatter (no usernames needed at inference)
formatter = OmniPromptFormatter("prompt.txt")

def ask(question):
    connection_status = "in_game"
    map_name = "Blackwater Docks"
    mode = "Deathmatch"
    players = [
        {"Username": "NeoFurySniper1681", "Health": 46, "Team": "orange"},
        {"Username": "Omni", "Health": 53, "Team": "aqua"},
        {"Username": "DarkSteelMaster", "Health": 40, "Team": "red"},
        {"Username": "", "Health": "null", "Team": ""},
        {"Username": "", "Health": "null", "Team": ""},
        {"Username": "", "Health": "null", "Team": ""},
        {"Username": "", "Health": "null", "Team": ""},
        {"Username": "", "Health": "null", "Team": ""}
    ]

    chat_log = f"FourBolt: {question}"

    prompt = formatter.assemble_inference_prompt(
        connection_status, map_name, mode, players, chat_log
    )

    # Tokenize and generate
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=100)

    response = tokenizer.decode(output[0], skip_special_tokens=True)
    print(f"Q: {question}")
    print(f"A: {response}")
    print("=" * 50)

# Example queries
ask("What is the Minirocket Tube?")
ask("Is friendly fire enabled in UYA?")
ask("How do you upgrade the N60 Storm?")

EOF

