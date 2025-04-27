#!/bin/bash
set -e
set -o pipefail

echo "🔍 Checking Python version..."
python3 --version

echo "🔍 Checking pip version..."
pip --version

echo "🔍 Checking Torch install and CUDA availability..."
python3 -c "import torch; print('Torch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"

echo "🔍 Checking Transformers install..."
python3 -c "import transformers; print('Transformers version:', transformers.__version__)"

echo "🔍 Checking BitsAndBytes install..."
python3 -c "import bitsandbytes as bnb; print('BitsAndBytes loaded successfully.')"

echo "🔍 Checking llama.cpp compilation..."
if [ -f "./llama.cpp/build/bin/llama-gguf" ]; then
  echo "llama.cpp compiled successfully."
else
  echo "❗ llama.cpp main binary missing."
  exit 1
fi

echo "🎉 All checks passed! Environment looks good."

