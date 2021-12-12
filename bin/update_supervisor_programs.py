
from common.arg_parse import initialize_start
from common.consts import VENDOR
# path = "/home/gilad/routers-stats-fetcher/docker/supervisord.conf"
from common.logs import Log

args = initialize_start(argsparse_params={'vendor': True, 'supervisor_path': True})
vendor = args.get('vendor')

if vendor == VENDOR.MIKROTIK:
    try:
        supervisor_path = args.get('supervisor_path')
        with open(supervisor_path, encoding='utf-8') as f:
            supervisor =f.read()
            supervisor = 'autostart=true'.join(supervisor.split('autostart=false'))
        with open(supervisor_path, 'w', encoding='utf-8') as f:
            f.write(supervisor)
    except Exception as ex:
        Log.exception(f'problem with update supervisor {str(ex)}')
