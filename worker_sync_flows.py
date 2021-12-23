#!/usr/bin/env python

'''
All rights reserved to Secunity 2021
'''
import time
import os

import datetime

from common.arg_parse import  initialize_start
from common.api_secunity import send_result
from common.consts import COMMENT, HEALTH_CHECK, SECUNITY
from common.health_check import read_health_check_files
from common.logs import Log
from common.schedulers import start_scheduler, add_job, shutdown_scheduler
from router_command import get_command_worker, parse_raw_sample
from router_command.add_remove_mikrotik import add_remove_flow_mikrotik

try:
    import jstyleson as json
except:
    import json

_scheduler = None


def compere_with_secunity_and_set(**kwargs):

    Log.debug('starting new iteration sync')
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
            suffix_url_path = 'sync_flows'
            send_params = {k: v for k, v in kwargs.items() if k not in con_params}
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



    Log.debug(f'finished iteration sync. success: {success}. error: "{error}".')
    return success
def _work_sync(**kwargs):
    compere_with_secunity_and_set(**kwargs)


def _work_health_check(**kwargs):
    Log.debug(f'starting new iteration. health check')

    worker, con_params = get_command_worker(**kwargs)

    if worker is not None:
        time_last_check_ok, time_last_check_error = read_health_check_files(**kwargs)

        success = True
        if not time_last_check_ok:
            success = False

        if success:
            now = datetime.datetime.utcnow()
            diff_seconds = (now - time_last_check_ok).seconds

            if diff_seconds > HEALTH_CHECK.SYNC_CAUSE_NO_HEALTH_FOR_LONG_TIME or\
                    (time_last_check_error and time_last_check_error > time_last_check_ok):
                success = False

        env_up_name = f'{kwargs.get("comment_flow_prefix",SECUNITY)}_UP'
        env_up = os.environ.get(env_up_name, 'False')
        if not success or env_up == 'False':
            Log.debug(f'timeout for health check, try to do sync')
            if not compere_with_secunity_and_set(**kwargs):
                worker.remove_all_flows()
                os.environ[env_up_name] = 'False'

            else:
                os.environ[env_up_name] = 'True'

    Log.debug(f'finished iteration. health check')

if __name__ == '__main__':
    argsparse_params = {_: True for _ in ('host', 'port', 'username', 'password', 'key_filename',
                                          'vendor', 'command_prefix', 'log', 'url', 'dump',)}
    args = initialize_start(argsparse_params=argsparse_params,
                            module=__file__.split('/')[-1].split('.')[0])

    start_scheduler(start=True)
    next_run_time = datetime.timedelta(seconds=2)
    add_job(func=_work_sync, interval=1115, func_kwargs=args, next_run_time=next_run_time)
    add_job(func=_work_health_check, interval=32, func_kwargs=args, next_run_time=next_run_time)
    try:
        while True:
            time.sleep(1)
    except Exception as ex:
        Log.warning(f'Stop signal received, shutting down')
        shutdown_scheduler()
        Log.warning('scheduler stopped')
        Log.warning('quiting')

