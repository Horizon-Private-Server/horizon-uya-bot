#!/bin/bash
set -e
set -o pipefail

export MODEL_DIR="$PWD/merged_model"
export OUTPUT_DIR="$PWD/uya_model"
export FINAL_GGUF_NAME="mistral7b_uya.gguf"
export FINAL_QUANT_NAME="mistral7b_uya_Q4_K_M.gguf"

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

echo "Running Docker to quantize GGUF model to 4-bit..."
docker run --rm -v "${OUTPUT_DIR}":/repo ghcr.io/ggerganov/llama.cpp:full --quantize "/repo/${FINAL_GGUF_NAME}" "/repo/${FINAL_QUANT_NAME}" "Q4_K_M"

if [ ! -f "${OUTPUT_DIR}/${FINAL_QUANT_NAME}" ]; then
    echo "Error: Quantization failed."
    exit 1
fi
echo "Quantization successful: ${OUTPUT_DIR}/${FINAL_QUANT_NAME}"

echo "Cleaning up intermediate files..."
rm -f "${OUTPUT_DIR}/${FINAL_GGUF_NAME}"

echo "Final 4-bit quantized GGUF model is ready at ${OUTPUT_DIR}/${FINAL_QUANT_NAME}"

