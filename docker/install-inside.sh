#!/bin/bash


if [ -f /opt/env-worker ]
then
  export $(cat /opt/env-worker | sed 's/#.*//g' | xargs)
fi


apt-get update --allow-releaseinfo-change && apt-get upgrade -y && apt-get autoremove -y  &&\
apt-get install -y nano procps supervisor git ntp wget ca-certificates cron

useradd -p "$PASSWORD" -u $USER_ID "$USER"
usermod -a -G root "$USER"

HOME="/home/$USER"
mkdir -p $HOME/.ssh
chown -R $USER $HOME
mv /opt/github-access-token $HOME/.ssh
chmod 400 $HOME/.ssh/github-access-token

echo "
Host github.com
 HostName github.com
 IdentityFile $HOME/.ssh/github-access-token
" >> $HOME/.ssh/config
chown -R $USER $HOME

for FOLDER in $SECUNITY_FOLDERS; do
  mkdir -p $FOLDER
  chmod +rw $FOLDER
  chown -R $USER $FOLDER
done


for FOLDER in $SECUNITY_PROGRAMS; do
  mkdir -p /opt/$FOLDER
  chown -R $USER /opt/$FOLDER
  rm -rf /opt/$FOLDER/*
done



echo "#!/bin/bash

bash -x /opt/start-ops.sh

PYTHONPATH=/opt/worker_statistics /opt/worker_statistics/venv/bin/python /opt/worker_statistics/bin/update_supervisor_programs.py

supervisord -c /etc/supervisor/supervisord.conf &

while :; do sleep 1; done
" > /entrypoint.sh
chmod 777 /entrypoint.sh




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
command=/opt/worker_set_remove_flow/venv/bin/python /opt/worker_set_remove_flow/worker_set_remove_flow.py
environment=PYTHONPATH=/opt/worker_set_remove_flow
autostart=false


[program:worker_statistics]
command=/opt/worker_statistics/venv/bin/python /opt/worker_statistics/worker_statistics.py
environment=PYTHONPATH=/opt/worker_statistics
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




chown -R $USER /opt
chown -R $USER /etc/supervisor



