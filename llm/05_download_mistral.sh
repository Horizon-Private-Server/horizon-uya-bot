export MODEL_DIR="./models/Mistral-7B-Instruct-v0.3"
export OUTPUT_DIR="./lora_output"

if [ ! -d "${MODEL_DIR}" ]; then
  mkdir -p models
  cd models
  echo "Downloading Mistral-7B-Instruct-v0.3 full model snapshot..."
  python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='mistralai/Mistral-7B-Instruct-v0.3', local_dir='./Mistral-7B-Instruct-v0.3', local_dir_use_symlinks=False, token='${HUGGINGFACE_HUB_TOKEN}')"
fi


