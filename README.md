# Creepfield Eyez

## Setup
After `git clone`, do these steps to get ready to run the code.

```bash
python3 -m venv ./venv
source venv/bin/activate
pip3 install -r requirements.txt 
```

## Run
After clean reboot of Raspberry Pi, do these steps to run the eyez.

```
sudo killall pigpiod

sudo pigpiod

source venv/bin/activate

nohup python3 -u scanner4.py >> scanner4.log 2>&1 &
tail -f scanner4.log
```
