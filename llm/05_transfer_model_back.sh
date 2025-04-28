
rm merged_model.tar.gz
scp -r -P ${VAST_PORT} root@${VAST_IP}:/workspace/merged_model.tar.gz .
