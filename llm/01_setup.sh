#!/bin/bash
set -e
set -o pipefail

pip install -r requirements.txt

echo "Updating apt and installing system packages..."
sudo apt update
sudo apt install -y git build-essential cmake libcurl4-openssl-dev

