#!/bin/bash
set -e
set -o pipefail

export MERGED_DIR="./merged_model"

python3 <<EOF
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load merged model
model = AutoModelForCausalLM.from_pretrained(
    "${MERGED_DIR}",
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True
)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    "${MERGED_DIR}",
    trust_remote_code=True
)

# Test generation
inputs = tokenizer("Hello, how are you?", return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))

# Print parameter count
print("Params:")
print(model.num_parameters() / 1e9, "B parameters")
EOF

