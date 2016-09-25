#!/bin/bash
# loop_bot.sh

python3.5 bot.py
while [[ $? -ne 0 ]]; do
  python3.5 bot.py
done
