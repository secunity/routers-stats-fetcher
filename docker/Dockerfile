FROM            python:3.7
MAINTAINER      Secunity LTD. (support@secunity.io)

ENV             SECUNITYAPP="routers-stats-fetcher"
ENV             PYTHONPATH=/opt/$SECUNITYAPP
ENV             SECUNITY_BRANCH="mikrotik"
ENV             vendor="mikrotik"
ENV             SECUNITY_FOLDERS="/etc/secunity /var/log/secunity"
ENV             PATH="/home/secunity/.local/bin:${PATH}"
ENV             SECUNITY_PROGRAMS="worker_statistics worker_set_remove_flow"

COPY            env-worker /opt
COPY            github-access-token /opt
COPY            install-inside.sh /opt

RUN             bash -x /opt/install-inside.sh && rm /opt/install-inside.sh

USER            secunity

COPY            install-inside-worker.sh /opt
RUN             bash -x /opt/install-inside-worker.sh &&\
                rm /opt/install-inside-worker.sh &&\
                rm /opt/env-worker

USER            root

WORKDIR         /opt/secunity

ENTRYPOINT      /entrypoint.sh


