#!/bin/bash
set -e
set -o pipefail

# 0. Define paths
export TRAIN_DATA="./base_facts.jsonl"
export MODEL_DIR="./models/Mistral-7B-Instruct-v0.3"
export OUTPUT_DIR="./lora_output"
export FINAL_GGUF="./mistral7b_uya.gguf"

# 1. Download Mistral-7B-Instruct-v0.3 (only if not already downloaded)
if [ ! -d "${MODEL_DIR}" ]; then
  mkdir -p models
  cd models
  echo "📥 Downloading Mistral-7B-Instruct-v0.3 full model snapshot..."
  python3 -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='mistralai/Mistral-7B-Instruct-v0.3', local_dir='./Mistral-7B-Instruct-v0.3', local_dir_use_symlinks=False, token='${HUGGINGFACE_HUB_TOKEN}')"
  cd ..
  echo
  echo
  echo
  echo
  echo
  echo
  echo "Download complete! Waiting 5 seconds."
  sleep 5
fi

# 2. Start LoRA fine-tuning
python <<EOF
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import load_dataset
from peft import get_peft_model, LoraConfig, TaskType

# Load base model
model = AutoModelForCausalLM.from_pretrained(
    "${MODEL_DIR}",
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained("${MODEL_DIR}", trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token  # Fix for padding if needed

# Load your dataset
dataset = load_dataset('json', data_files='${TRAIN_DATA}', split='train')

# Preprocessing: Format examples into [INST] ... [/INST]
def format_prompt(example):
    instruction = example['instruction']
    input_text = example['input']
    if input_text.strip() != "":
        prompt = f"[INST] {instruction} {input_text} [/INST]"
    else:
        prompt = f"[INST] {instruction} [/INST]"
    return {
        "prompt": prompt,
        "response": example["output"]
    }

dataset = dataset.map(format_prompt)

# Tokenization
def tokenize_function(example):
    full_prompt = example["prompt"]
    full_response = example["response"]
    prompt_plus_response = full_prompt + " " + full_response
    tokenized = tokenizer(prompt_plus_response, padding="max_length", truncation=True, max_length=4096)
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

dataset = dataset.map(tokenize_function, remove_columns=["instruction", "input", "output", "prompt", "response"])

# Apply LoRA
config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

model = get_peft_model(model, config)

# Training args
training_args = TrainingArguments(
    output_dir="${OUTPUT_DIR}",
    per_device_train_batch_size=2,  # or 4 if you want slight speed boost without hurting quality
    gradient_accumulation_steps=8,
    warmup_steps=20,  # a little longer warmup
    logging_steps=10,
    save_steps=50,
    save_total_limit=1,
    num_train_epochs=5,  # more epochs to memorize 551 examples
    learning_rate=1e-4,  # safer learning rate for LoRA
    bf16=True,
    optim="paged_adamw_8bit",
    report_to="none",
    save_strategy="steps",
    logging_dir="${OUTPUT_DIR}/logs",
    push_to_hub=False,
)

trainer = Trainer(
    model=model,
    train_dataset=dataset,
    args=training_args,
    tokenizer=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
)

# Start training
trainer.train()

# Save final LoRA model
model.save_pretrained("${OUTPUT_DIR}")
EOF

# 3. Quantize and compile into GGUF 4-bit
./llama.cpp/build/bin/llama-gguf \
    --outtype q4_0 \
    --outfile "${FINAL_GGUF}" \
    --lora "${OUTPUT_DIR}" \
    --model "${MODEL_DIR}"

# 4. Done!
echo "🎉 LoRA fine-tuning, merging, and quantization completed!"
echo "🎯 Your 4-bit GGUF file is at: ${FINAL_GGUF}"

