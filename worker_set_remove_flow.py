#!/usr/bin/env python

'''
All rights reserved to Secunity 2021
'''
import time

from bin.arg_parse import  initialize_start
from common.api_secunity import send_result
from common.logs import log
from common.utils import get_con_params, _start_scheduler_utils
from router_command import get_vendor_class
try:
    import jstyleson as json
except:
    import json

_scheduler = None


def remove_flows(outgoing_flows_to_remove, worker, **kwargs):
    raw_samples = worker.work(**kwargs)
    for _ in outgoing_flows_to_remove:
        _id = next((flow.get('id') for flow in raw_samples if flow.get('comment') == _), None)
        try:
            worker.remove_flow_with_id(_id=_id)
        except Exception as ex:
            pass
    # data = [_.get('comment') for _ in outgoing_flows_to_add]

    try:
        suffix_url_path = 'update_remove'
        sent, msg = send_result(data={'data': outgoing_flows_to_remove}, suffix_url_path=suffix_url_path, **kwargs)
    except Exception as ex:
        log.error(ex)

def add_flows(outgoing_flows_to_add, worker, **kwargs):
    for _ in outgoing_flows_to_add:
        try:
            worker.add_flow(flow_to_add=_)
        except Exception as ex:
            log.error(ex)

    data = [_.get('comment') for _ in outgoing_flows_to_add]
    try:
        suffix_url_path = 'update_set'
        sent, msg = send_result(data={'data': data}, suffix_url_path=suffix_url_path, **kwargs)

    except Exception as ex:
        log.error(ex)



def _work(**kwargs):
    log.debug('starting new iteration')
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


    log.debug(f'finished iteration. success: {success}. error: "{error}".')


def _start_scheduler(**kwargs):
    from apscheduler.triggers.interval import IntervalTrigger
    _start_scheduler_utils(_work, IntervalTrigger(seconds=15), **kwargs)




if __name__ == '__main__':

    args = initialize_start()
    # _start_scheduler(**args)
    _work(**args)
    try:
        while True:
            time.sleep(1)
    except Exception as ex:
        log.warning(f'Stop signal recieved, shutting down scheduler: {str(ex)}')
        _scheduler.shutdown()
        log.warning('scheduler stopped')
        log.warning('quiting')
