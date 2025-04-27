#!/bin/bash
set -e
set -o pipefail

pip install bitsandbytes accelerate peft transformers datasets trl huggingface_hub safetensors
pip install sentencepiece protobuf

echo "🛠️ Updating apt and installing system packages..."
sudo apt update
sudo apt install -y git build-essential cmake libcurl4-openssl-dev

echo "📥 Cloning llama.cpp..."
# Clone llama.cpp if not already cloned
if [ ! -d "llama.cpp" ]; then
  git clone https://github.com/ggerganov/llama.cpp.git
fi

cd llama.cpp

echo "🔨 Preparing build directory..."
# Create build directory if not already created
mkdir -p build
cd build

echo "⚙️ Configuring build (CURL disabled)..."
# Configure with CURL explicitly disabled (still safer to have libcurl present)
cmake .. -DLLAMA_CURL=OFF

echo "🔨 Building llama.cpp..."
# Build the project
cmake --build . --config Release

echo "✅ llama.cpp built successfully!"
echo "🔗 Compiled binaries are in ./llama.cpp/build/bin/"

