#!/usr/bin/env python

'''
All rights reserved to Secunity 2021
'''
import time

import datetime

from common.arg_parse import  initialize_start
from common.api_secunity import send_result
from common.consts import COMMENT
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




def _work(**kwargs):
    Log.debug('starting new iteration')
    success, error, con_params = get_con_params(**kwargs)

    if success:
        success, vendor_cls, vendor = get_vendor_class(**kwargs)

    try:
        suffix_url_path = 'set_flows'
        send_params = {k: v for k, v in kwargs.items() if k not in con_params}
        send_params['url_method'] = 'GET'
        success, body = send_result(success=success, suffix_url_path=suffix_url_path, error=error, **send_params)
        if success:
            outgoing_flows_to_add, outgoing_flows_to_remove = body.get('outgoing_flows_to_add'), body.get('outgoing_flows_to_remove')
        else:
            error = f'failed to send results back: {body}'
    except Exception as ex:
        error = f'failed to send results back: {str(ex)}'
        success = False
    if success:
        worker = vendor_cls(**con_params)

        add_remove_flow_mikrotik(outgoing_flows_to_add=outgoing_flows_to_add,
                                 outgoing_flows_to_remove=outgoing_flows_to_remove,
                                 worker=worker, con_params=con_params, **kwargs)



    Log.debug(f'finished iteration. success: {success}. error: "{error}".')



if __name__ == '__main__':
    argsparse_params = {_: True for _ in ('host', 'port', 'username', 'password', 'key_filename',
                                          'vendor', 'command_prefix', 'log', 'url', 'dump')}
    args = initialize_start(argsparse_params=argsparse_params,
                            module=__file__.split('/')[-1].split('.')[0])

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

