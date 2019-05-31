# The Other Townsend

This code lives on a server at Digital Ocean and serves up files for a Telegram bot called @theothertownsend

## initial setup

```
git clone ; cd othertownsend

mkdir logs

sudo chgrp -R www-data .
sudo chmod -R g+rw .

cat "TOKEN = 'BLAHBLAH' > .config

virtualenv -p python3 venv
. venv/bin/activate
pip install -r requirements.txt

sudo supervisorctl reload 
```