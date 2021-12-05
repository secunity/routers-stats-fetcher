import datetime
import os
import shlex
import re
import time
from subprocess import check_output

from clog import log
from share import SETTING


_defaults = {
    'interval_minutes': 60,
    'repo': 'https://github.com/secunity/routers-stats-fetcher.git',
    'script_dir': os.path.dirname(os.path.realpath(__file__)),
    'git_regex': re.compile('Updating', re.IGNORECASE),
    'supervisor_executor_name': 'secunity-worker',
}


def _check_upgrade(**kwargs):
    log.debug('checking for code upgrade')
    script_dir = kwargs.get('script_dir') or _defaults['script_dir']
    log.debug(f'script folder: {script_dir}')

    command = 'git fetch'
    try:
        output = check_output(shlex.split(command), cwd=script_dir)
    except Exception as ex:
        log.exception(f'failed to issue command: {command}. error: {str(ex)}')
        return False

    command = f'git checkout $SECUNITY_BRANCH'
    try:
        output = check_output(shlex.split(command), cwd=script_dir)
    except Exception as ex:
        log.exception(f'failed to issue command: {command}. error: {str(ex)}')
        return False

    command = 'git pull'
    try:
        output = check_output(shlex.split(command), cwd=script_dir)
        if isinstance(output, bytes):
            output = output.decode('utf-8')
    except Exception as ex:
        log.exception(f'failed to issue command: {command}. error: {str(ex)}')
        return False

    if not output or not isinstance(output, str):
        log.error(f'failed to issue git commands')
        return False

    log.debug('git commands issued')
    try:
        git_regex = kwargs.get('git_regex') or _defaults['git_regex']
        output = output.split('\n')
        match = next((git_regex.match(_) for _ in output), None)
    except Exception as ex:
        log.exception(f'no regex is available for parsing git response')
        return False

    if match:
        log.debug('code changes were detected, restating secunity-executor')
        executor_name = kwargs.get('supervisor_executor_name') or _defaults['supervisor_executor_name']
        command = f'supervisorctl stop {executor_name}'
        stopped = False
        try:
            log.debug(f'stopping secunity executor. command: {command}')
            output = check_output(shlex.split(command))
            if isinstance(output, bytes):
                output = output.decode('utf-8')
            if executor_name in output:
                stopped = True

            command = f"find {script_dir} -name '*.pyc' -delete"
            try:
                output = check_output(command)
            except Exception as ex:
                pass
        except Exception as ex:
            log.exception(f'failed to perform command: {command}. error: {str(ex)}')
            stopped = True
            return False
        finally:
            if stopped:
                command = f'supervisorctl start {executor_name}'
                try:
                    output = check_output(shlex.split(command))
                except Exception as ex:
                    pass
    else:
        log.debug('no code update detected')
    return True


def _parse_config(config, **kwargs):
    if not os.path.isfile(config):
        log.error(f'missing config file: {config}')
        raise ValueError(f'missing config file: {config}')

    try: import jstyleson as json
    except: import json
    with open(config, 'r') as f:
        return json.load(f)


_scheduler = None


def _start_scheduler(**kwargs):
    interval_minutes = int(kwargs.get('interval_minutes') or _defaults['interval_minutes'])

    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.executors.pool import ThreadPoolExecutor
    import pytz

    log.debug('initializing scheduler and jobs')
    global _scheduler
    _scheduler = BackgroundScheduler(executors={'default': ThreadPoolExecutor(10)},
                                     job_defaults={'max_instances': 1},
                                     timezone=pytz.utc)

    _scheduler.add_job(func=_check_upgrade,
                       trigger=IntervalTrigger(minutes=interval_minutes),
                       kwargs=kwargs,
                       max_instances=1,
                       next_run_time=datetime.datetime.utcnow() + datetime.timedelta(seconds=1))

    _scheduler.start()
    log.debug('scheduler and jobs initialized')


__args__ = {
    'logfile': None,
    'verbose': False,
    'stdout': False,
    'stderr': False,
    'interval_minutes': _defaults['interval_minutes'],
    'repo': _defaults['repo'],
    'script_dir': '/opt/$SECUNITYAPP',
    'supervisor_executor_name': _defaults['supervisor_executor_name']
}


def _parse_args(args):
    for key, _default in copy.deepcopy(__args__).items():
        value = args.get(key)
        if value is None:
            value = os.environ.get(f'SECUNITY_UPDATER_{key.upper()}')
            if value is None:
                value = _default
            args[key] = value
    return args


def _init_(**kwargs):
    SETTING.update(type=SETTING.TYPE.LOG, update={k: v for k, v in kwargs.items()
                                                  if k in ('logfile', 'verbose',
                                                           'to_stdout', 'stdout', 'to_stderr', 'stderr')})
    log.init()

if __name__ == '__main__':
    import argparse
    import copy

    parser = argparse.ArgumentParser(description='Secunity On-Prem Agent code updater')

    parser.add_argument('-l', '--logfile', type=str, help='File to log to', default=None)
    parser.add_argument('-v', '--verbose', type=bool, help='Indicates whether to log verbose data', default=None)

    parser.add_argument('--stdout', type=str, help='Log messages to stdout', default=None)
    parser.add_argument('--stderr', type=str, help='Log error messages to stderr', default=None)

    parser.add_argument('-i', '--interval_minutes', type=int, help='Code changes checker interval (minutes)', default=None)

    parser.add_argument('-r', '--repo', type=str, help='Code git repo', default=None)
    parser.add_argument('-d', '--script_dir', type=str, help='Current script folder', default=None)
    parser.add_argument('-en', '--supervisor_executor_name', type=str,
                        help='The name of the supervisord executor name running the agent', default=None)

    args = parser.parse_args()
    args = _parse_args(vars(args))
    _init_(**args)

    log.debug('bla bla')
    log.debug('assd')

    _start_scheduler(**args)

    try:
        while True:
            time.sleep(1)
    except Exception as ex:
        log.warning(f'Stop signal recieved, shutting down scheduler: {str(ex)}')
        _scheduler.shutdown()
        log.warning('scheduler stopped')
        log.warning('quiting')