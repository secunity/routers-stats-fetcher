FROM python:3.6
# FROM python:3.6-alpine

RUN apt-get update && apt-get upgrade -y && apt-get autoremove -y &&\
    apt-get install -y git &&\
    cd /opt && git clone https://github.com/secunity/routers-stats-fetcher.git /opt/routers-stats-fetcher &&\
    python3 -m pip install --upgrade pip setuptools &&\
    python3 -m pip install -r /opt/routers-stats-fetcher/requirements.txt


ENV PATH="/opt/routers-stats-fetcher:${PATH}"
ENV PYTHONPATH=/opt/routers-stats-fetcher

WORKDIR /opt/routers-stats-fetcher

CMD ["python3", "/opt/routers-stats-fetcher/worker.py"]




