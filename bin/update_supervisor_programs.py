import logging
import os

from common.consts import VENDOR
# path = "/home/gilad/routers-stats-fetcher/docker/supervisord.conf"
from common.logs import Log

path = "/etc/supervisor/supervisord.conf"
vendor = os.getenv('vendor')
if vendor == VENDOR.MIKROTIK:
    try:
        with open(path, encoding='utf-8') as f:
            supervisor =f.read()
            supervisor = 'autostart=true'.join(supervisor.split('autostart=false'))
        with open(path, 'w', encoding='utf-8') as f:
            f.write(supervisor)
    except Exception as ex:
        Log.exception(f'problem with update supervisor {str(ex)}')
