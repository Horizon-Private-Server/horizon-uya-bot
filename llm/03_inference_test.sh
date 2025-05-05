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
formatter = OmniPromptFormatter()

def ask(question):
    chat_log = f"FourBolt: {question}"

    prompt = formatter.assemble_inference_prompt(chat_log)

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

