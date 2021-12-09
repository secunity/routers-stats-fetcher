#!/bin/bash

if [ -f /opt/env-worker ]
then
  export $(cat /opt/env-worker | sed 's/#.*//g' | xargs)
fi

ssh-keyscan github.com >> ~/.ssh/known_hosts
rm -rf $PYTHONPATH/*
git clone git@github.com:secunity/routers-stats-fetcher.git /opt/worker_statistics
git clone git@github.com:secunity/routers-stats-fetcher.git /opt/worker_set_remove_flow

python3 -m pip install --upgrade pip setuptools
python3 -m pip install --upgrade virtualenv

cd /opt/worker_statistics
git checkout $SECUNITY_BRANCH
python3 -m virtualenv venv
source venv/bin/activate
pip install --upgrade pip setuptools
git fetch --all
git pull
pip install -r requirements.txt
deactivate

cd /opt/worker_set_remove_flow
git checkout $SECUNITY_BRANCH
python3 -m virtualenv venv
source venv/bin/activate
pip install --upgrade pip setuptools
git fetch --all
git pull
pip install -r requirements.txt
deactivate


rm /etc/supervisor/supervisord.conf
cat << 'EOF' >> /etc/supervisor/supervisord.conf
; supervisor config file

[unix_http_server]
file=/tmp/supervisor.sock   ; (the path to the socket file)
chmod=0700                       ; sockef file mode (default 0700)

[supervisord]
nodaemon=true
logfile=/var/log/supervisor/supervisord.log ; (main log file;default $CWD/supervisord.log)
pidfile=/var/run/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
childlogdir=/var/log/supervisor            ; ('AUTO' child log dir, default $TEMP)

; the below section must remain in the config file for RPC
; (supervisorctl/web interface) to work, additional interfaces may be
; added by defining them in separate rpcinterface: sections
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///tmp/supervisor.sock ; use a unix:// URL  for a unix socket


[program:worker_set_remove_flow]
command=/opt/secunity/venv/bin/python /opt/secunity/worker_set_remove_flow.py
environment=PYTHONPATH=/opt/secunity
autostart=false


[program:worker_statistics]
command=/opt/secunity/venv/bin/python /opt/secunity/worker_statistics.py
environment=PYTHONPATH=/opt/secunity
autostart=true


[program:ntp]
command=bash -c "sleep 5 && service ntp start"

; The [include] section can just contain the "files" setting.  This
; setting can list multiple files (separated by whitespace or
; newlines).  It can also contain wildcards.  The filenames are
; interpreted as relative to this file.  Included files *cannot*
; include files themselves.


# [include]
# files = /etc/supervisor/conf.d/*.conf
EOF
