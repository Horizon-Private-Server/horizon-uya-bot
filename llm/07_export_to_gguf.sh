#!/bin/bash
set -e
set -o pipefail

export MODEL_DIR="$PWD/full_finetune_output"
export OUTPUT_DIR="$PWD/final_model"
export FINAL_GGUF_NAME="mistral7b_uya.gguf"
export FINAL_QUANT_NAME="mistral7b_uya_Q4_K_M.gguf"


rm -rf ${OUTPUT_DIR}
mkdir -p "${OUTPUT_DIR}"

echo "Copying fine-tuned model to output directory..."
cp -r "${MODEL_DIR}"/* "${OUTPUT_DIR}/"

echo "Running Docker to convert Huggingface model to GGUF..."
docker run --rm -v "${OUTPUT_DIR}":/repo ghcr.io/ggerganov/llama.cpp:full --convert /repo --outfile "/repo/${FINAL_GGUF_NAME}" --outtype f32

if [ ! -f "${OUTPUT_DIR}/${FINAL_GGUF_NAME}" ]; then
    echo "Error: GGUF conversion failed."
    exit 1
fi
echo "GGUF conversion successful: ${OUTPUT_DIR}/${FINAL_GGUF_NAME}"

rm -rf llama.cpp/
git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
mkdir build
cd build
cmake ..
cmake --build . --config Release
cd ../..

echo "Finished building llama-cpp!"
sleep 2

./llama.cpp/build/bin/llama-quantize ${OUTPUT_DIR}/${FINAL_GGUF_NAME} ${OUTPUT_DIR}/${FINAL_QUANT_NAME} Q4_K_M

echo "Final 4-bit quantized GGUF model is ready at ${OUTPUT_DIR}/${FINAL_QUANT_NAME}"

