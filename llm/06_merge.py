import torch
from transformers import AutoModelForCausalLM
from peft import PeftModel

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    "./models/Mistral-7B-Instruct-v0.3",
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True
)

# Fix for PEFT expecting .base_model
base_model.base_model = base_model.model

# Load LoRA adapter
lora_model = PeftModel.from_pretrained(
    model=base_model,
    model_id="./lora_output",
    torch_dtype=torch.bfloat16,
    device_map=None  # Must be None during LoRA load
)

# Merge LoRA into base
merged_model = lora_model.merge_and_unload()

# Save merged model
merged_model.save_pretrained("./merged_model", safe_serialization=True)

