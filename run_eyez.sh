#!/bin/bash
cd /home/creepfield/eyez
sudo killall pigpiod
sudo pigpiod
source venv/bin/activate
python3 eyez.py >> eyez.log 2>&1



