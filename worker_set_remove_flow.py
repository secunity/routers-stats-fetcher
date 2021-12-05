#!/usr/bin/env python

'''
All rights reserved to Secunity 2021
'''
import datetime

from common.utils import log, ERROR, send_result, _parse_env_vars, _set_args_types, _parse_config, _DEFAULTS, _cnf
from router_command import get_vendor_class
import requests
try:
    import jstyleson as json
except:
    import json

_scheduler = None


_SEND_RESULT_DEFAULTS = {
    'url_host': '172.20.0.103',
    'url_scheme': 'http',
    'url_path': 'fstats1/v1.0.0/in',
    'url_method': 'POST'
}

def get_con_params(**kwargs):
    try:
        success, error, raw_samples = True, None, []

        con_params = {
            k: v for k, v in kwargs.items()
            if not k.startswith('url') and k not in ('identifier',)
        }
    except Exception as ex:
        error = f'failed to parse connection params: {str(ex)}'
        log.exception(error)
        success = False
        raw_samples = ERROR.CONERROR
    return success, raw_samples, error, con_params


def _work(**kwargs):
    log.debug('starting new iteration')
    success, raw_samples, error, con_params = get_con_params(**kwargs)

    if success:
        success, raw_samples, vendor_cls, vendor = get_vendor_class(**kwargs)

    try:
        send_params = {k: v for k, v in kwargs.items() if k not in con_params}
        identifier = kwargs.get('identifier')
        res = requests.get(f'http://172.20.0.103:5000/in/flows/set/{identifier}')
        outgoing_flows = res.json()
        outgoing_flows_to_add, outgoing_flows_to_remove = outgoing_flows.get('outgoing_flows_to_add'), outgoing_flows.get('outgoing_flows_to_remove')
        pass
    except Exception as ex:
        error = f'failed to send results back: {str(ex)}'
        success = False
    if success:
        worker = vendor_cls(**con_params)
        if outgoing_flows_to_add:
            for _ in outgoing_flows_to_add:
                try:
                    worker.add_flow(flow_to_add=_)
                except Exception as ex:
                    print(ex)
            data = [_.get('comment') for _ in outgoing_flows_to_add]
            try:
                res = requests.post(url=f'http://172.20.0.103:5000/in/flows/update_set/{identifier}', json={'data': data})
            except Exception as ex:
                print(ex)

        if outgoing_flows_to_remove:
            raw_samples = worker.work(**con_params)
            for _ in outgoing_flows_to_remove:
                _id = next((flow.get('id') for flow in raw_samples if flow.get('comment') == _), None)
                worker.remove_flow_with_id(_id=_id)

            data = [_.get('comment') for _ in outgoing_flows_to_add]
            try:
                res = requests.post(url=f'http://172.20.0.103:5000/in/flows/update_remove/{identifier}', json={'data': data})
            except Exception as ex:
                print(ex)

    log.debug(f'finished iteration. success: {success}. error: "{error}". len(samples string): {len(raw_samples)}')


def _start_scheduler(**kwargs):
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.executors.pool import ThreadPoolExecutor
    import pytz

    log.debug('initializing scheduler and jobs')
    global _scheduler
    _scheduler = BackgroundScheduler(executors={'default': ThreadPoolExecutor(30)},
                                     job_defaults={'max_instances': 1},
                                     timezone=pytz.utc)

    _scheduler.add_job(func=_work,
                       trigger=IntervalTrigger(minutes=15),
                       kwargs=kwargs,
                       max_instances=1,
                       next_run_time=datetime.datetime.utcnow() + datetime.timedelta(seconds=1))

    _scheduler.start()
    log.debug('scheduler and jobs initialized')


if __name__ == '__main__':
    import argparse
    import time
    import copy

    parser = argparse.ArgumentParser(description='Secunity On-Prem Agent')

    parser.add_argument('-c', '--config', type=str, help='Config file (overriding all other options)',
                        default=_DEFAULTS['config'])

    parser.add_argument('-l', '--logfile', type=str, help='File to log to', default=None)
    parser.add_argument('-v', '--verbose', type=bool, help='Indicates whether to log verbose data', default=False)
    parser.add_argument('-d', '--dump', type=str, help='File path to dump results')

    parser.add_argument('--to_stdout', '--stdout', type=str, help='Log messages to stdout', default=False)
    parser.add_argument('--to_stderr', '--stderr', type=str, help='')

    parser.add_argument('--identifier', '--id', type=str, help='Device ID', default=None)

    parser.add_argument('-s', '--host', '--ip', type=str, help='Router IP', default=None)
    parser.add_argument('-p', '--port', type=int, default=None, help='SSH port')
    parser.add_argument('-n', '--vendor', type=str, default='mikrotik', help='The Vendor of the Router')
    # parser.add_argument('-n', '--vendor', type=str, default='cisco', help='The Vendor of the Router')
    parser.add_argument('-u', '--user', '--username', type=str, default=None, help='SSH user')
    parser.add_argument('-w', '--password', type=str, default=None, help='SSH password')
    parser.add_argument('-k', '--key_filename', type=str, default=None, help='SSH Key Filename')

    parser.add_argument('--command_prefix', type=str, default=None,
                        help='The prefix to use when sending commands to the Router using SSH (for instance "cli" in Juniper)')

    parser.add_argument('--url', type=str, help='The URL to use for remove server', default=None)
    parser.add_argument('--url_scheme', type=str, help='Remote server URL scheme', default=None)
    parser.add_argument('--url_host', type=str, help='Remote server URL hostname', default=None)
    parser.add_argument('--url_port', type=int, help='Remote server URL port', default=5000)
    parser.add_argument('--url_path', type=str, help='Remote server URL path', default=None)
    parser.add_argument('--url_method', type=str, help='Remote server URL method', default=None)

    args = parser.parse_args()
    args = vars(args)
    args = _parse_env_vars(args)

    config = args['config']
    if config:
        config = _parse_config(config)
        args.update(config)
    args = _set_args_types(args)

    _cnf.update({k: v for k, v in copy.deepcopy(args).items()})

    _start_scheduler(**args)

    try:
        while True:
            time.sleep(1)
    except Exception as ex:
        log.warning(f'Stop signal recieved, shutting down scheduler: {str(ex)}')
        _scheduler.shutdown()
        log.warning('scheduler stopped')
        log.warning('quiting')
