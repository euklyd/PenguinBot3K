#!/bin/bash
# loop_bot.sh

python3.5 bot.py
ERROR=$?
while [[ ${ERROR} -ne 0 ]]; do
  echo "[$(date "+%Y-%m-%d %H:%M:%S")] Bot exited with error code ${ERROR}; restarting."
  python3.5 bot.py
done
