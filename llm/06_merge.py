from transformers import AutoModelForCausalLM
from peft import PeftModel

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    "./models/Mistral-7B-Instruct-v0.3",
    torch_dtype="auto",
    trust_remote_code=True,
    device_map="auto"
)

# Load LoRA
lora_model = PeftModel.from_pretrained(
    base_model,
    "./lora_output"
)

# Merge LoRA into base model
merged_model = lora_model.merge_and_unload()

# Save merged model
merged_model.save_pretrained("./merged_model")

