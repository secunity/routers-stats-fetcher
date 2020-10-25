FROM python:3.6
# FROM python:3.6-alpine

ADD entrypoint.sh /

RUN apt-get update && apt-get upgrade -y && apt-get autoremove -y &&\
    apt-get install -y git &&\
    mkdir -p /etc/supervisor &&\
    git clone https://github.com/secunity/routers-stats-fetcher.git /opt/routers-stats-fetcher &&\
    python3 -m pip install --upgrade pip setuptools &&\
    python3 -m pip install supervisor &&\
    python3 -m pip install -r /opt/routers-stats-fetcher/requirements.txt &&\
    chmod 777 /entrypoint.sh &&\
    chmod 777 /opt/routers-stats-fetcher/worker.py &&\
    chmod 777 /opt/routers-stats-fetcher/upgrader.py

ADD supervisord.conf /etc/supervisor

ENV PATH="/opt/routers-stats-fetcher:${PATH}"
ENV PYTHONPATH=/opt/routers-stats-fetcher

WORKDIR /opt/routers-stats-fetcher

CMD ["/entrypoint.sh"]

#  rm -rf /opt/routers-stats-fetcher
