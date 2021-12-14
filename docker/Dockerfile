FROM            python:3.7
MAINTAINER      Secunity LTD. (support@secunity.io)

ENV             SECUNITYAPP="routers-stats-fetcher"
ENV             PYTHONPATH=/opt/$SECUNITYAPP
ENV             SECUNITY_BRANCH="sync_flows"
ENV             SECUNITY_FOLDERS="/etc/secunity /var/log/secunity"
ENV             PATH="/home/secunity/.local/bin:${PATH}"
ENV             SECUNITY_PROGRAMS="worker_statistics worker_set_remove_flow worker_sync_flows"

COPY            env-worker /opt
COPY            github-access-token /opt
COPY            install-inside.sh /opt

RUN             bash -x /opt/install-inside.sh && rm /opt/install-inside.sh

USER            secunity

COPY            install-inside-user.sh /opt
RUN             bash -x /opt/install-inside-user.sh &&\
                rm /opt/install-inside-user.sh &&\
                rm /opt/env-worker

USER            root

WORKDIR         /opt/secunity

ENTRYPOINT      /entrypoint.sh


