#!/usr/bin/env python

'''
All rights reserved to Secunity 2021
'''
import datetime
import os
from collections import Iterable
import ipaddress

from common.utils import log, ERROR, send_result, _parse_env_vars, _set_args_types, _parse_config, _DEFAULTS, _cnf
from router_command import get_vendor_class
from router_command.exabgp_router import CiscoCommandWorker, JuniperCommandWorker, AristaCommandWorker
from router_command.mikrotik_router import MikroTikApiCommandWorker

try: import jstyleson as json
except: import json




_scheduler = None



def parse_raw_sample(success, raw_samples, vendor):
    if success:
        try:
            log.debug('formatting results')
            if not isinstance(raw_samples, str) and vendor != 'mikrotik':
                if isinstance(raw_samples, Iterable):
                    raw_samples = '\n'.join(raw_samples if isinstance(raw_samples, list) else [_ for _ in raw_samples])
            log.debug('results formatted')
        except Exception as ex:
            error = f'failed to format results: {str(ex)}'
            log.exception(error)
            success = False
            raw_samples = ERROR.FORMATTING
        error = None

    else:
        error = raw_samples
        raw_samples = []

    return success, raw_samples, error

def get_raw_sample(vendor_cls, con_params, host,  **kwargs):
    try:
        success, error = True, None
        worker = vendor_cls(**con_params)
        raw_samples = worker.work(**con_params)
        # to remove dummy
        raw_samples = raw_samples[1:]
        log.debug(f'finished querying device {host}. response length: {len(raw_samples)}')
        dump = kwargs.get('dump')
        if dump:
            log.debug(f'writing dump results to "{dump}"')
            try:
                lines = [_ for _ in raw_samples if _.strip()]
                lines.insert(0,
                             f"Time: {datetime.datetime.utcnow().strftime(_DEFAULTS['datetime_format'])} (local: {datetime.datetime.now().strftime(_DEFAULTS['datetime_format'])})")
                lines.append('')
                lines = '\n'.join(lines)
                with open(dump, 'a') as f:
                    f.write(lines)
            except Exception as ex:
                log.exception(f'failed to write results to dump file "{dump}": "{str(ex)}"')
    except Exception as ex:
        error = f"failed to read router {con_params.get('host')}: {str(ex)}"
        log.exception(error)
        success = False
        raw_samples = ERROR.CONERROR

    return success, raw_samples, error



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

    if success:
        success, raw_samples, error = get_raw_sample(vendor_cls=vendor_cls, con_params=con_params, **kwargs)

    if success:
        success, raw_samples, error = parse_raw_sample(success, raw_samples, vendor)

    try:
        send_params = {k: v for k, v in kwargs.items() if k not in con_params}
        sent, msg = send_result(success=success, raw_samples=raw_samples, error=error, **send_params)
        if not sent:
            success, error = False, msg or f'failed to send message'
    except Exception as ex:
        error = f'failed to send results back: {str(ex)}'
        success = False

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
                       trigger=IntervalTrigger(minutes=1),
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

    parser.add_argument('-c', '--config', type=str, help='Config file (overriding all other options)', default=_DEFAULTS['config'])

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
