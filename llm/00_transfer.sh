scp -P ${VAST_PORT} *.py *.txt *.sh root@${VAST_IP}:/workspace

scp -r -P ${VAST_PORT} training_data root@${VAST_IP}:/workspace
