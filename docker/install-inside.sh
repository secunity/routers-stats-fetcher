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


chown -R $USER /opt
chown -R $USER /etc/supervisor



