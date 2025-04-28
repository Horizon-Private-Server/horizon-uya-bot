rm -rf lora_output/

scp -r -P ${VAST_PORT} root@${VAST_IP}:/workspace/lora_output .

