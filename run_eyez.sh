#!/bin/bash
cd /home/creepfield/eyez
sudo killall pigpiod
sudo pigpiod
source venv/bin/activate
python3 scanner4.py >> scanner4.log 2>&1



