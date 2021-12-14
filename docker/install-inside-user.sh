#!/bin/bash

if [ -f /opt/env-worker ]
then
  export $(cat /opt/env-worker | sed 's/#.*//g' | xargs)
fi

ssh-keyscan github.com >> ~/.ssh/known_hosts
rm -rf /opt/worker_statistics/ /opt/worker_set_remove_flow
mkdir /opt/worker_statistics
mkdir /opt/worker_set_remove_flow
mkdir /opt/worker_sync_flows
git clone git@github.com:secunity/routers-stats-fetcher.git /opt/worker_statistics
git clone git@github.com:secunity/routers-stats-fetcher.git /opt/worker_set_remove_flow
git clone git@github.com:secunity/routers-stats-fetcher.git /opt/worker_sync_flows

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

cd /opt/worker_sync_flows
git checkout $SECUNITY_BRANCH
python3 -m virtualenv venv
source venv/bin/activate
pip install --upgrade pip setuptools
git fetch --all
git pull
pip install -r requirements.txt
deactivate
