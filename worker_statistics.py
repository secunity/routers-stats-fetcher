#!/usr/bin/env python

'''
All rights reserved to Secunity 2021
'''
import time
from collections import Iterable
import datetime
from common.arg_parse import initialize_start
from common.api_secunity import send_result
from common.consts import VENDOR
from common.logs import Log
from common.schedulers import start_scheduler, add_job, shutdown_scheduler
from common.utils import get_con_params, ERROR

from router_command import get_vendor_class

try:
    import jstyleson as json
except:
    import json

_scheduler = None


def parse_raw_sample(success, raw_samples, vendor):
    try:
        Log.debug('formatting results')
        if not isinstance(raw_samples, str) and vendor != 'mikrotik':
            if isinstance(raw_samples, Iterable):
                raw_samples = '\n'.join(raw_samples if isinstance(raw_samples, list) else [_ for _ in raw_samples])
        Log.debug('results formatted')
    except Exception as ex:
        error = f'failed to format results: {str(ex)}'
        Log.exception(error)
        success = False
        raw_samples = ERROR.FORMATTING
    error = None

    return success, raw_samples, error


def get_raw_sample(vendor_cls, con_params, host, **kwargs):
    try:
        success, error = True, None
        worker = vendor_cls(**con_params)
        raw_samples = worker.work(**con_params)
        Log.debug(f'finished querying device {host}. response length: {len(raw_samples)}')

    except Exception as ex:
        error = f"failed to read router {con_params.get('host')}: {str(ex)}"
        Log.exception(error)
        success = False
        raw_samples = ERROR.CONERROR

    return success, raw_samples, error


def _work(**kwargs):
    Log.debug('starting new iteration')
    success, error, con_params = get_con_params(**kwargs)

    if success:
        success, vendor_cls, vendor = get_vendor_class(**kwargs)

    if success:
        success, raw_samples, error = get_raw_sample(vendor_cls=vendor_cls, con_params=con_params, **kwargs)

    if success and vendor != VENDOR.MIKROTIK:
        success, raw_samples, error = parse_raw_sample(success, raw_samples, vendor)

    try:
        suffix_url_path = 'send_statistics'
        send_params = {k: v for k, v in kwargs.items() if k not in con_params}
        sent, msg = send_result(success=success, data={'samples': raw_samples}, suffix_url_path=suffix_url_path,
                                error=error, **send_params)
        if not sent:
            success, error = False, msg or f'failed to send message'
    except Exception as ex:
        error = f'failed to send results back: {str(ex)}'
        success = False

    Log.debug(f'finished iteration. success: {success}. error: "{error}".')


if __name__ == '__main__':
    argsparse_params = {_: True for _ in ('host', 'port', 'username', 'password', 'key_filename',
                                          'vendor', 'command_prefix', 'log', 'url', 'dump')}

    args = initialize_start(argsparse_params=argsparse_params)

    start_scheduler(start=True)
    add_job(func=_work, interval=60, func_kwargs=args, next_run_time=datetime.timedelta(seconds=2))

    try:
        while True:
            time.sleep(1)
    except Exception as ex:
        Log.warning(f'Stop signal received, shutting down')
        shutdown_scheduler()
        Log.warning('scheduler stopped')
        Log.warning('quiting')


#
# def _start_scheduler(**kwargs):
#     from apscheduler.triggers.interval import IntervalTrigger
#     _start_scheduler_utils(_work, IntervalTrigger(minutes=1), **kwargs)
#
#
#
# if __name__ == '__main__':
#
#     args = initialize_start()
#     _start_scheduler(**args)
#
#     try:
#         while True:
#             time.sleep(1)
#     except Exception as ex:
#         log.warning(f'Stop signal recieved, shutting down scheduler: {str(ex)}')
#         _scheduler.shutdown()
#         log.warning('scheduler stopped')
#         log.warning('quiting')
