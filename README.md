# The Other Townsend


## @theothertownsend
This code lives on a server at Digital Ocean and serves up files for a Telegram bot, [t.me/OtherTownsendBot](t.me/OtherTownsendBot)

It accepts these commands:

/start
/set <n seconds>			# get OT updates every <n seconds>
/unset						# unset automatic updates
/loc						# get current location
/feeling					# an iconic report of current mood
/sleep						# an iconic report of how they slept

## @devothertowbsend
The dev bot lives here: [t.me/OtherTownsendBot](t.me/OtherTownsendBot)

/start
/set <n seconds>			# get OT updates every <n seconds>
/unset						# unset automatic updates
/loc						# get current location
/feeling					# an iconic report of current mood
/sleep						# an iconic report of how they slept



## initial setup

```
git clone https://github.com/douglasgoodwin/othertownsend.git ; 
cd othertownsend

mkdir logs

sudo chgrp -R www-data .
sudo chmod -R g+rw .

cat "TOKEN = 'BLAHBLAH' > _config.py

virtualenv -p python3 venv
. venv/bin/activate
pip install -r requirements.txt

sudo supervisorctl reload 
```