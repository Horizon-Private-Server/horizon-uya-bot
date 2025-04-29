
rm -rf full_finetune_output
scp -r -P ${VAST_PORT} root@${VAST_IP}:/workspace/full_finetune_output .
