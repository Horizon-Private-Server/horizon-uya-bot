#!/bin/bash
set -e
set -o pipefail

# Build all.jsonl
output_file="all.jsonl"
input_dir="training_data"

> "$output_file"
find "$input_dir" -type f -name '*.jsonl' -print0 | while IFS= read -r -d '' file; do
    cat "$file" >> "$output_file"
done

# Remove empty lines from the final file
grep -v '^$' "$output_file" > temp && mv temp "$output_file"


