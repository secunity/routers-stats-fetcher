#!/usr/bin/env python

'''
All rights reserved to Secunity 2021
'''
import time
from collections import Iterable
import datetime
from common.arg_parse import initialize_start
from common.api_secunity import send_result
from common.consts import VENDOR, ERROR
from common.logs import Log
from common.schedulers import start_scheduler, add_job, shutdown_scheduler

from router_command import get_command_worker, parse_raw_sample

try:
    import jstyleson as json
except:
    import json

_scheduler = None



def _work(**kwargs):
    Log.debug('starting new iteration')
    try:
        worker, con_params = get_command_worker(**kwargs)
        if worker:
            raw_samples = worker.work(**kwargs)

            raw_samples, error = parse_raw_sample(raw_samples, **kwargs)
        else:
            error = True
    except Exception as ex:
        error = f'error in get_command_worker. error: "{str(ex)}".'


    if error is not None:
        success = False
    else:
        try:
            suffix_url_path = 'send_statistics'
            send_params = {k: v for k, v in kwargs.items() if k not in con_params}
            success, msg = send_result( data={'samples': raw_samples}, suffix_url_path=suffix_url_path,
                                     **send_params)
            if not success:
                 error = msg or f'failed to send message'
        except Exception as ex:
            error = f'failed to send results back: {str(ex)}'
            success = False

    Log.debug(f'finished iteration. success: {success}. error: "{error}".')


if __name__ == '__main__':
    argsparse_params = {_: True for _ in ('host', 'port', 'username', 'password', 'key_filename',
                                          'vendor', 'command_prefix', 'log', 'url', 'dump')}

    args = initialize_start(argsparse_params=argsparse_params,
                            module=__file__.split('/')[-1].split('.')[0])
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
