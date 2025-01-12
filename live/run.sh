#!/bin/bash
source /home/ubuntu/.bashenv
cd /home/ubuntu/horizon-uya-bot/live
screen -S live -X quit;
screen -dmS live bash -lc 'source /home/ubuntu/.bashenv && cd /home/ubuntu/horizon-uya-bot/live && rm -rf logs && /home/ubuntu/anaconda3/bin/python -u livetrackerserver.py'
