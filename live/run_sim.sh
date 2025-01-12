#!/bin/bash
source /home/ubuntu/.bashenvsim
cd /home/ubuntu/horizon-uya-bot/live
screen -S livesim -X quit;
screen -dmS livesim bash -lc 'source /home/ubuntu/.bashenvsim && cd /home/ubuntu/horizon-uya-bot/live && rm -rf logs && /home/ubuntu/anaconda3/bin/python -u livetrackerserver.py'
