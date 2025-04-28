#!/bin/bash
set -e
set -o pipefail

pip install bitsandbytes accelerate peft transformers datasets trl huggingface_hub safetensors sentencepiece protobuf

echo "Updating apt and installing system packages..."
sudo apt update
sudo apt install -y git build-essential cmake libcurl4-openssl-dev

echo "Cloning ggml-org/llama.cpp..."
if [ ! -d "llama.cpp" ]; then
  git clone https://github.com/ggml-org/llama.cpp.git
fi

cd llama.cpp

echo "Preparing build directory..."
mkdir -p build
cd build

echo "Configuring build (CURL disabled)..."
cmake .. -DLLAMA_CURL=OFF

echo "Building llama.cpp..."
cmake --build . --config Release

cd ../..

echo "Downloading convert_hf_to_gguf.py..."
wget https://raw.githubusercontent.com/ggml-org/llama.cpp/master/convert_hf_to_gguf.py -O convert_hf_to_gguf.py

echo "Setup complete."

