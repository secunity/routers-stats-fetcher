#!/usr/bin/env python

'''
All rights reserved to Secunity 2021
'''
import time

import datetime

from common.arg_parse import  initialize_start
from common.api_secunity import send_result
from common.consts import COMMENT
from common.health_check import read_health_check, health_check_file_path, error_health_check_file_path
from common.logs import Log
from common.schedulers import start_scheduler, add_job, shutdown_scheduler
from common.utils import get_con_params
from router_command import get_vendor_class
from router_command.add_remove_mikrotik import add_remove_flow_mikrotik

try:
    import jstyleson as json
except:
    import json

_scheduler = None

def get_command_worker(**kwargs):
    success, error, con_params = get_con_params(**kwargs)

    if success:
        success, vendor_cls, vendor = get_vendor_class(**kwargs)
    if success:

        worker = vendor_cls(**con_params)
        return worker, con_params
    return False, False

def compere_with_secunity_and_set(**kwargs):
    Log.debug('starting new iteration')


    worker, con_params = get_command_worker(**kwargs)
    try:
        suffix_url_path = 'sync_flows'
        send_params = {k: v for k, v in kwargs.items() if k not in con_params}
        raw_samples = worker.work(**kwargs)
        raw_samples_ids = [_.get(COMMENT) for _ in raw_samples]
        data = {'flows_ids': raw_samples_ids}
        success, body = send_result(suffix_url_path=suffix_url_path, data=data, worker=worker, **send_params)
        if success:
            outgoing_flows_to_add, outgoing_flows_to_remove = body.get('outgoing_flows_to_add'), body.get('outgoing_flows_to_remove')
        else:
            error = f'failed to send results back: {body}'

    except Exception as ex:
        error = f'failed to send results back: {str(ex)}'
        success = False
    if success:

        add_remove_flow_mikrotik(outgoing_flows_to_add=outgoing_flows_to_add,
                                 outgoing_flows_to_remove=outgoing_flows_to_remove,
                                 worker=worker, con_params=con_params, **kwargs)



    Log.debug(f'finished iteration. success: {success}. error: "{error}".')

def _work_sync(**kwargs):
    compere_with_secunity_and_set(**kwargs)

sync_cause_no_health_for_long = 60*1212
def _work_health_check(**kwargs):
    worker, con_params = get_command_worker(**kwargs)

    if worker is not None and worker.__class__.__name__ == 'MikroTikApiCommandWorker':
        time_last_check = read_health_check(file_path=health_check_file_path)
        time_last_check_error = read_health_check(file_path=error_health_check_file_path)
        now = datetime.datetime.utcnow()
        diff_seconds = (now - time_last_check).seconds
        if diff_seconds > sync_cause_no_health_for_long or time_last_check_error > time_last_check:
            worker.remove_all_flows()


if __name__ == '__main__':
    argsparse_params = {_: True for _ in ('host', 'port', 'username', 'password', 'key_filename',
                                          'vendor', 'command_prefix', 'log', 'url', 'dump')}
    args = initialize_start(argsparse_params=argsparse_params,
                            module=__file__.split('/')[-1].split('.')[0])

    start_scheduler(start=True)
    add_job(func=_work_sync, interval=1115, func_kwargs=args, next_run_time=datetime.timedelta(seconds=2))
    add_job(func=_work_health_check, interval=32, func_kwargs=args, next_run_time=datetime.timedelta(seconds=2))
    try:
        while True:
            time.sleep(1)
    except Exception as ex:
        Log.warning(f'Stop signal received, shutting down')
        shutdown_scheduler()
        Log.warning('scheduler stopped')
        Log.warning('quiting')

