#!/bin/bash
set -e
set -o pipefail

# Build all.jsonl
output_file="all.jsonl"
input_dir="training_data"

# Empty the output file first
> "$output_file"

# Find all .jsonl files recursively and concatenate them
find "$input_dir" -type f -name '*.jsonl' -print0 | while IFS= read -r -d '' file; do
    cat "$file" >> "$output_file"
    echo >> "$output_file"  # ensure a newline between files
done

export TRAIN_DATA="./all.jsonl"
export MODEL_DIR="./models/Mistral-7B-Instruct-v0.3"
export OUTPUT_DIR="./lora_output"

if [ ! -d "${MODEL_DIR}" ]; then
  mkdir -p models
  cd models
  echo "Downloading Mistral-7B-Instruct-v0.3 full model snapshot..."
  python3 -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='mistralai/Mistral-7B-Instruct-v0.3', local_dir='./Mistral-7B-Instruct-v0.3', local_dir_use_symlinks=False, token='${HUGGINGFACE_HUB_TOKEN}')"
  cd ..
  echo "Download complete. Waiting 5 seconds."
  sleep 5
fi

python <<EOF
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import load_dataset
from peft import get_peft_model, LoraConfig, TaskType

model = AutoModelForCausalLM.from_pretrained(
    "${MODEL_DIR}",
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained("${MODEL_DIR}", trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

dataset = load_dataset('json', data_files='${TRAIN_DATA}', split='train')

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

def tokenize_function(example):
    full_prompt = example["prompt"]
    full_response = example["response"]
    prompt_plus_response = full_prompt + " " + full_response
    tokenized = tokenizer(prompt_plus_response, padding="max_length", truncation=True, max_length=4096)
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

dataset = dataset.map(tokenize_function, remove_columns=["instruction", "input", "output", "prompt", "response"])

config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

model = get_peft_model(model, config)

training_args = TrainingArguments(
    output_dir="${OUTPUT_DIR}",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    warmup_steps=20,
    logging_steps=10,
    save_steps=50,
    save_total_limit=1,
    num_train_epochs=5,
    learning_rate=1e-4,
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

trainer.train()

model.save_pretrained("${OUTPUT_DIR}")
EOF


