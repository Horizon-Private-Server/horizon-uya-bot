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

echo "Installing docker..."

echo "Setup complete."

# Remove any old versions
sudo apt-get remove -y docker docker-engine docker.io containerd runc || true

# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up Docker stable repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index again
sudo apt-get update

# Install Docker
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable and start Docker
sudo systemctl enable docker
sudo systemctl start docker

echo "Docker installation complete."
