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
    prompt = f"[INST] You are an AI answering UYA multiplayer questions. {question} [/INST]"
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

