#!/bin/bash
set -e
set -o pipefail

# Build all.jsonl
output_file="all.jsonl"
input_dir="training_data"

> "$output_file"
find "$input_dir" -type f -name '*.jsonl' -print0 | while IFS= read -r -d '' file; do
    cat "$file" >> "$output_file"
    echo >> "$output_file"
done

export TRAIN_DATA="./all.jsonl"
export MODEL_DIR="./models/Mistral-7B-Instruct-v0.3"
export OUTPUT_DIR="./full_finetune_output"

if [ ! -d "${MODEL_DIR}" ]; then
  mkdir -p models
  cd models
  echo "Downloading base model..."
  python3 -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='mistralai/Mistral-7B-Instruct-v0.3', local_dir='./Mistral-7B-Instruct-v0.3', local_dir_use_symlinks=False, token='${HUGGINGFACE_HUB_TOKEN}')"
  cd ..
  sleep 5
fi

python3 <<EOF
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM, DefaultDataCollator
from datasets import load_dataset
from tqdm import tqdm

# Load full model
model = AutoModelForCausalLM.from_pretrained(
    "${MODEL_DIR}",
    torch_dtype=torch.bfloat16,
    device_map="cuda:0",
    trust_remote_code=True
)
model = torch.compile(model)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("${MODEL_DIR}", trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

# Load dataset
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

dataset = dataset.map(format_prompt, num_proc=4, desc="Formatting prompts")

def tokenize_function(batch):
    prompts = batch["prompt"]
    responses = batch["response"]
    prompt_plus_response = [p + " " + r for p, r in zip(prompts, responses)]
    tokenized = tokenizer(
        prompt_plus_response,
        padding="max_length",
        truncation=True,
        max_length=1024
    )
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

dataset = dataset.map(
    tokenize_function,
    remove_columns=["instruction", "input", "output", "prompt", "response"],
    batched=True,
    batch_size=1000,
    num_proc=4,
    desc="Tokenizing dataset"
)
dataset = dataset.with_format("torch")

# Dataloader
batch_size = 2

# Adjust if memory allows more
loader = DataLoader(
    dataset,
    batch_size=batch_size,
    shuffle=True,
    collate_fn=DefaultDataCollator(),
    pin_memory=True
)

# Optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)

# Scheduler
#num_epochs = 50
#warmup_steps = 100

num_epochs = 5  # <<<<< reduced from 50 to 5
warmup_steps = 10  # <<<<< adjust warmup to match shorter run

total_steps = len(loader) * num_epochs

def lr_scheduler(step):
    if step < warmup_steps:
        return step / warmup_steps
    return 1.0

scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=lr_scheduler)

# Training
model.train()
overall_progress = tqdm(total=total_steps, desc="Total Progress", position=0, leave=True)

for epoch in range(num_epochs):
    print(f"Starting epoch {epoch+1}/{num_epochs}")
    for batch in loader:
        optimizer.zero_grad()
        input_ids = batch["input_ids"].cuda()
        attention_mask = batch["attention_mask"].cuda()
        labels = batch["labels"].cuda()
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        scheduler.step()

        overall_progress.update(1)
        overall_progress.set_postfix({"loss": loss.item()})

overall_progress.close()

# Save the full finetuned model
model.save_pretrained("${OUTPUT_DIR}")
tokenizer.save_pretrained("${OUTPUT_DIR}")

# Inference check
model.eval()
prompt = "What is UYA?"
inputs = tokenizer(f"[INST] {prompt} [/INST]", return_tensors="pt").to(model.device)
with torch.no_grad():
    output = model.generate(**inputs, max_new_tokens=100)
print("\n=== Inference Test ===")
print(tokenizer.decode(output[0], skip_special_tokens=True))
print("======================")
EOF

