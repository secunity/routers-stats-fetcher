FROM        python:3.6
MAINTAINER  Secunity LTD. (support@secunity.io)

ENV         SECUNITYAPP="routers-stats-fetcher"
ENV         PATH="/opt/$SECUNITYAPP:${PATH}"
ENV         PYTHONPATH=/opt/$SECUNITYAPP
ENV         SECUNITY_BRANCH="dump1"

ADD         entrypoint.sh /


RUN         apt-get update && apt-get upgrade -y && apt-get autoremove -y &&\
            apt-get install -y git python3-pip &&\
            mkdir -p /etc/supervisor &&\
            git clone https://github.com/secunity/routers-stats-fetcher.git /opt/$SECUNITYAPP &&\
            cd /opt/$SECUNITYAPP &&\
            git checkout $SECUNITY_BRANCH &&\
            python3 -m pip install --upgrade pip setuptools &&\
            python3 -m pip install supervisor &&\
            python3 -m pip install -r /opt/$SECUNITYAPP/requirements.txt &&\
            chmod 777 /entrypoint.sh &&\
            chmod 777 /opt/$SECUNITYAPP/worker.py &&\
            chmod 777 /opt/$SECUNITYAPP/upgrader.py

ADD         supervisord.conf /etc/supervisor

WORKDIR     /opt/$SECUNITYAPP

ENTRYPOINT  ["/entrypoint.sh"]

