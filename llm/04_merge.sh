#!/bin/bash
set -e
set -o pipefail

export BASE_MODEL_DIR="./models/Mistral-7B-Instruct-v0.3"
export LORA_DIR="./lora_output"
export MERGED_DIR="./merged_model"

rm -rf $MERGED_DIR

python3 <<EOF
import torch
from transformers import AutoModelForCausalLM
from peft import PeftModel

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    "${BASE_MODEL_DIR}",
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True
)

# Fix for PEFT expecting .base_model
base_model.base_model = base_model.model

# Load LoRA adapter
lora_model = PeftModel.from_pretrained(
    model=base_model,
    model_id="${LORA_DIR}",
    torch_dtype=torch.bfloat16,
    device_map=None  # Must be None during LoRA load
)

# Merge LoRA into base
merged_model = lora_model.merge_and_unload()

# Save merged model
merged_model.save_pretrained("${MERGED_DIR}", safe_serialization=False)
EOF

# After merge, copy tokenizer files
cp "${BASE_MODEL_DIR}/tokenizer.json" "${MERGED_DIR}/"
cp "${BASE_MODEL_DIR}/tokenizer_config.json" "${MERGED_DIR}/"
cp "${BASE_MODEL_DIR}/special_tokens_map.json" "${MERGED_DIR}/"
cp "${BASE_MODEL_DIR}/tokenizer.model" "${MERGED_DIR}/"

# Optional: overwrite generation config again just in case
cp "${BASE_MODEL_DIR}/generation_config.json" "${MERGED_DIR}/"

echo "Done Merging!"
ls $MERGED_DIR
