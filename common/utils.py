import ipaddress
import sys
import logging
import os
import json
import datetime

from common.consts import BOOL_TYPES
from common.logs import log

_DEFAULTS = {
    'config': 'routers-stats-fetcher.conf',
    # 'config': '/opt/routers-stats-fetcher/routers-stats-fetcher.conf',
    'datetime_format': '%Y-%m-%d %H:%M:%S',
}


__BOOL_TYPES__ = (True, False,)

_cnf = {'__log_init__': False}




def _start_scheduler_utils(func, time_interval, **kwargs):
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.executors.pool import ThreadPoolExecutor
    import pytz

    log.debug('initializing scheduler and jobs')
    global _scheduler
    _scheduler = BackgroundScheduler(executors={'default': ThreadPoolExecutor(30)},
                                     job_defaults={'max_instances': 1},
                                     timezone=pytz.utc)

    _scheduler.add_job(func=func,
                       trigger=time_interval,
                       # trigger=IntervalTrigger(seconds=15),
                       kwargs=kwargs,
                       max_instances=1,
                       next_run_time=datetime.datetime.utcnow() + datetime.timedelta(seconds=1))

    _scheduler.start()
    log.debug('scheduler and jobs initialized')

class ERROR:
    CONERROR = 'conerror'
    INVALID_CON_PARAMS = 'invalid-con-params'
    UNSUPPORTED_VENBDOR = 'unsupported-vendor'
    FORMATTING = 'formatting'

    __ALL__ = (CONERROR, INVALID_CON_PARAMS, UNSUPPORTED_VENBDOR, FORMATTING)

    @classmethod
    def has(cls, value):
        return value in cls.__ALL__


def get_con_params(**kwargs):
    try:
        success, error = True, None

        con_params = {
            k: v for k, v in kwargs.items()
            if not k.startswith('url') and k not in ('identifier',)
        }
    except Exception as ex:
        error = f'failed to parse connection params: {str(ex)}'
        log.exception(error)
        success = False
    return success, error, con_params

def _to_bool(x):
    if x is None:
        return None
    elif x in __BOOL_TYPES__:
        return x
    elif not isinstance(x, str):
        pass
    elif x.lower() == 'true':
        return True
    elif x.lower() == 'false':
        return False
    error = f'invalid bool: "{x}"'
    log.error(error)
    raise ValueError(error)


def _parse_vendor(vendor):
    if not vendor:
        return 'cisco'
    vendor = vendor.strip().lower()
    if vendor in ('cisco', 'juniper', 'arista', 'mikrotik'):
        return vendor

    error = f'invalid vendor: "{vendor}"'
    log.exception(error)
    raise ValueError(error)
def parse_bool(x: object, parse_str:dict =  False):
    if x is None:
        return None
    elif x in BOOL_TYPES:
        return x
    elif parse_str and isinstance(x, str):
        x = x.strip(' \r\n\t')
        if x.lower() == 'true':
            return True
        elif x.lower() == 'false':
            return False
    error = f'invalid bool: "{x}"'
    raise ValueError(error)


def parse_ip(ip, throw=False):
    try:
        ip = ipaddress.IPv4Address(ip)
        return str(ip)
    except Exception as ex:
        if throw:
            raise ex
        return None


# def _parse_ip(ip, throw=False):
#     try:
#         ip = ipaddress.IPv4Address(ip)
#         return str(ip)
#     except Exception as ex:
#         if throw:
#             log.exception(f'failed to parse ip: "{ip}". error: {str(ex)}')
#             raise ex
#         return None
#
# _types = {
#     str: lambda x: x if isinstance(x, str) else str(x),
#     int: lambda x: x if isinstance(x, int) else int(x),
#     bool: _to_bool,
#     'vendor': _parse_vendor,
#     'ip': _parse_ip,
# }
#
# _conf_keys = {
#     'config': str,
#     'logfile': str,
#     'verbose': bool,
#     'dump': str,
#     'to_stderr': bool,
#     'to_stdout': bool,
#
#     'identifier': str,
#     'host': 'ip',
#     'port': int,
#     'vendor': 'vendor',
#     'username': str,
#     'password': str,
#     'command_prefix': str,
#
#     'url_scheme': str,
#     'url_host': 'ip',
#     'url_port': int,
#     'url_path': str,
#     'url_method': str,
# }
#
# def _parse_env_vars(args):
#     args.update({
#         _: os.environ.get(f'SECUNITY_{_.upper()}')
#         for _ in ('config',
#                   'logfile', 'verbose', 'dump', 'to_stderr', 'to_stdout',
#                   'identifier',
#                   'host', 'port', 'vendor', 'username', 'password', 'command_prefix',
#                   'url_scheme', 'url_host', 'url_port', 'url_path', 'url_method',)
#         if args.get(_) is None and os.environ.get(f'SECUNITY_{_.upper()}') is not None
#     })
#
#     return args
#
#

