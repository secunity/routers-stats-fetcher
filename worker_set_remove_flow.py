#!/usr/bin/env python

'''
All rights reserved to Secunity 2021
'''
import time

import datetime

from common.arg_parse import  initialize_start
from common.api_secunity import send_result
from common.consts import ACTION_FLOW_STATUS
from common.logs import Log
from common.schedulers import start_scheduler, add_job, shutdown_scheduler
from common.utils import get_con_params
from router_command import get_vendor_class
try:
    import jstyleson as json
except:
    import json

_scheduler = None


def remove_flows(outgoing_flows_to_remove, worker, **kwargs):
    raw_samples = worker.work(**kwargs)
    for outgoing_flow_id in outgoing_flows_to_remove:
        _id = next((flow.get('id') for flow in raw_samples if flow.get('comment') == outgoing_flow_id), None)
        try:
            if _id is not None:
                worker.remove_flow_with_id(_id=_id)
        except Exception as ex:
            pass
        try:
            suffix_url_path = f"flows/{ACTION_FLOW_STATUS.REMOVED}/{outgoing_flow_id}"
            sent, msg = send_result(suffix_url_path=suffix_url_path, **kwargs)
        except Exception as ex:
            Log.error(ex)


def add_flows(outgoing_flows_to_add, worker, **kwargs):
    for _ in outgoing_flows_to_add:
        try:
            worker.add_flow(flow_to_add=_)
        except Exception as ex:
            Log.error(ex)

        try:
            suffix_url_path = f"flows/{ACTION_FLOW_STATUS.APPLIED}/{_.get('comment')}"
            sent, msg = send_result(suffix_url_path=suffix_url_path, **kwargs)

        except Exception as ex:
            Log.error(ex)


def _work(**kwargs):
    Log.debug('starting new iteration')
    success, error, con_params = get_con_params(**kwargs)

    if success:
        success, vendor_cls, vendor = get_vendor_class(**kwargs)

    try:
        suffix_url_path = 'set_flows'
        send_params = {k: v for k, v in kwargs.items() if k not in con_params}
        send_params['url_method'] = 'GET'
        sent, body = send_result(success=success, suffix_url_path=suffix_url_path, error=error, **send_params)
        outgoing_flows_to_add, outgoing_flows_to_remove = body.get('outgoing_flows_to_add'), body.get('outgoing_flows_to_remove')
    except Exception as ex:
        error = f'failed to send results back: {str(ex)}'
        success = False
    if success:
        worker = vendor_cls(**con_params)
        if outgoing_flows_to_add:
            add_flows(outgoing_flows_to_add=outgoing_flows_to_add, worker=worker, **kwargs)

        if outgoing_flows_to_remove:
            remove_flows(outgoing_flows_to_remove=outgoing_flows_to_remove, worker=worker, **kwargs)


    Log.debug(f'finished iteration. success: {success}. error: "{error}".')



if __name__ == '__main__':
    argsparse_params = {_: True for _ in ('host', 'port', 'username', 'password', 'key_filename',
                                          'vendor', 'command_prefix', 'log', 'url', 'dump')}
    args = initialize_start(argsparse_params=argsparse_params,
                            module = __file__.split('/')[-1].split('.')[0])

    start_scheduler(start=True)
    add_job(func=_work, interval=15, func_kwargs=args, next_run_time=datetime.timedelta(seconds=2))
    try:
        while True:
            time.sleep(1)
    except Exception as ex:
        Log.warning(f'Stop signal received, shutting down')
        shutdown_scheduler()
        Log.warning('scheduler stopped')
        Log.warning('quiting')

