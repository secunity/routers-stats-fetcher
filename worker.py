#!/usr/bin/env python

'''
All rights reserved to Secunity 2021
'''
import datetime
import os
import sys
from abc import ABC, abstractmethod
import logging
from collections import Iterable
import ipaddress

import paramiko
import requests
try: import jstyleson as json
except: import json


SSH_DEFAULTS = {
    'port': 22,
    'warn': False,
    'pty': True,
    'timeout': 30
}

_SEND_RESULT_DEFAULTS = {
    'url_host': 'api.secunity.io',
    'url_scheme': 'https',
    'url_path': 'fstats1/v1.0.0/in',
    'url_method': 'POST'
}

_DEFAULTS = {
    'config': '/opt/routers-stats-fetcher/routers-stats-fetcher.conf',
    'datetime_format': '%Y-%m-%d %H:%M:%S',
}


__BOOL_TYPES__ = (True, False,)

_cnf = {'__log_init__': False}

_scheduler = None


def _init_logger(logfile=None, verbose=False, to_stdout=False, to_stderr=False, **kwargs):
    logger = logging.getLogger(__name__)
    if _cnf['__log_init__']:
        return logger

    log_level = logging.DEBUG if verbose else logging.WARNING
    logger.setLevel(log_level)

    handlers = []
    if to_stdout:
        handlers.append(logging.StreamHandler(sys.stdout))
    if to_stderr:
        handlers.append(logging.StreamHandler(sys.stderr))
    if logfile:
        handlers.append(logging.FileHandler(logfile))

    for handler in handlers:
        handler.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(lineno)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if handlers:
        _cnf['__log_init__'] = True
    return logger

class logMeta(type):

    def __getattr__(self, item):
        if item.upper() in self._methods:
            return getattr(self._log(), item.lower())

class log(metaclass=logMeta):

    _logger = None

    _methods = ('CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'WARN', 'INFO', 'DEBUG', 'EXCEPTION')

    @classmethod
    def _log(cls):
        if not cls._logger:
            cls._logger = _init_logger(**_cnf)
        return cls._logger


class CommandWorker(ABC):

    def __init__(self, credentials=None, **kwargs):
        self._credentials = self._parse_credentials(credentials=credentials, **kwargs)

    def _parse_credentials(self, credentials=None, **kwargs):
        if not credentials:
            credentials = {}
        credentials.update({k: v for k, v in SSH_DEFAULTS.items() if k not in credentials})

        for key, keys in {'host': ('host', 'ip'),
                          'user': ('user', 'username'),
                          'password': ('password', 'pass'),
                          'key_filename': ('key_filename', 'file')
                          }.items():
            value = credentials.get(key)
            if not value:
                value = next((credentials.pop(_) for _ in keys if _ != key and credentials.get(_)), None)
                if not value:
                    value = next((kwargs[_] for _ in [key] + [__ for __ in keys] if kwargs.get(_)), None)
                if value:
                    credentials[key] = value

        return credentials

    def _validate_credentials(self, credentials):
        if not credentials['host']:
            raise ValueError('SSH host ("--host") was not specified')
        if credentials['user'] and not (credentials.get('password') or credentials.get('key_filename')):
            raise ValueError('SSH user was specified without password or key_filename')

    def _ssh_to_paramiko_params(self, params):
        self._validate_credentials(params)
        result = {
            'hostname': params['host'],
            'port': params['port'],
            'username': params['user'],
            'allow_agent': True,
            'look_for_keys': params['look_for_keys'] if params.get('look_for_keys') in (True, False) else False
        }

        if params.get('password'):
            result['password'] = params['password']
        else:
            result['key_filename'] = params['key_filename']
        if params.get('timeout'):
            result['timeout'] = params['timeout']

        return result

    def _generate_connection(self, params, **kwargs):
        look_for_keys = [_.pop('look_for_keys', None) for _ in (kwargs, params)]
        offset = next((i + 1 for i, _ in enumerate(look_for_keys) if _ in (True, False)), None)
        params['look_for_keys'] = look_for_keys[offset - 1] if isinstance(offset, int) else False

        connection = paramiko.SSHClient()
        connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        params = self._ssh_to_paramiko_params(params)
        connection.connect(**params)
        return connection

    def perform_cli_command(self, credentials, command=None, exec_command=None, **kwargs):
        if not command and not exec_command:
            raise ValueError('either "command" or "exec_command" must be specified')

        connection = self._generate_connection(credentials, **kwargs)
        try:
            if not exec_command:
                if not command.endswith('\n'):
                    command = f'{command}\n'
                def _exec_command(_connection, _command, **_kwargs):
                    stdin, stdout, stderr = _connection.exec_command(_command)

                    result = stdout.readlines()
                    lines = [_.rstrip('\r\n') for _ in result]
                    return lines
                exec_command = _exec_command

            return exec_command(connection, command, **kwargs)
        finally:
            connection.close()

    @abstractmethod
    def get_stats_from_router(self, credentials, **kwargs):
        pass

    def work(self, credentials=None, **kwargs):
        credentials = self._parse_credentials(credentials, **kwargs) if credentials else self._credentials

        stats = self.get_stats_from_router(credentials, **kwargs)
        return stats


class CiscoCommandWorker(CommandWorker):

    def get_stats_from_router(self, credentials, **kwargs):
        # command = 'sh flowspec ipv4 detail'
        command = 'show flowspec vrf all ipv4 detail'
        result = self.perform_cli_command(credentials=credentials, command=command, **kwargs)
        return result


class JuniperCommandWorker(CommandWorker):

    def get_stats_from_router(self, credentials, **kwargs):
        command = 'show firewall filter detail __flowspec_default_inet__'
        command_prefix = _cnf.get('command_prefix')
        if command_prefix:
            if isinstance(command_prefix, str):
                command = f'{command_prefix} {command}'
            elif isinstance(command_prefix, bool) or command_prefix == 1:
                command = f'cli {command}'
        result = self.perform_cli_command(credentials=credentials, command=command, **kwargs)
        return result


class AristaCommandWorker(CommandWorker):

    def get_stats_from_router(self, credentials, **kwargs):
        command = 'sh flow-spec ipv4'
        result = self.perform_cli_command(credentials=credentials, command=command, **kwargs)
        return result


def _parse_identifier(identifier=None, **kwargs):
    if not identifier:
        identifier = kwargs.get('device_identifier') or kwargs.get('device') or kwargs.get('key')
    return identifier


def send_result(success, raw_samples, url=None, error=None, **kwargs):
    log.debug('starting message sending')
    identifier = _parse_identifier(**kwargs)

    if not url:
        url_params = {k: kwargs[k] if kwargs.get(k) or isinstance(kwargs.get(k), bool) else v
                      for k, v in _SEND_RESULT_DEFAULTS.items()}

        url_port = url_params.get('url_port') or kwargs.get('url_port')
        if url_port:
            url_params['url_host'] = f"{url_params['url_host']}:{url_port}"
        url = '{url_scheme}://{url_host}/{url_path}'.format(**url_params)
        kwargs.update(url_params)

    url = f"{url.rstrip('/ ')}/{identifier}/"
    log.debug(f'sending result for identifier {identifier} to {url}')

    result = {
        'success': success,
        'error': error,
        'samples': raw_samples,
        'time': datetime.datetime.utcnow().isoformat()
    }

    method = kwargs.get('url_method') or _SEND_RESULT_DEFAULTS['url_method']
    func = getattr(requests, method.lower())
    response = func(url=url, json=result)
    return 200 <= response.status_code <= 210, error


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


class ERROR:
    CONERROR = 'conerror'
    INVALID_CON_PARAMS = 'invalid-con-params'
    UNSUPPORTED_VENBDOR = 'unsupported-vendor'
    FORMATTING = 'formatting'

    __ALL__ = (CONERROR, INVALID_CON_PARAMS, UNSUPPORTED_VENBDOR, FORMATTING)

    @classmethod
    def has(cls, value):
        return value in cls.__ALL__


def _work(**kwargs):
    log.debug('starting new iteration')
    success, error, raw_samples = True, None, []
    try:
        con_params = {
            k: v for k, v in kwargs.items()
            if not k.startswith('url') and k not in ('identifier',)
        }
    except Exception as ex:
        error = f'failed to parse connection params: {str(ex)}'
        log.exception(error)
        success = False
        raw_samples = ERROR.CONERROR

    if success:
        vendor = kwargs['vendor'].strip().lower()
        host = kwargs['host']
        log.debug(f'starting to query device "{host}", vendor: "{vendor}"')
        if vendor == 'cisco':
            vendor_cls = CiscoCommandWorker
        elif vendor == 'juniper':
            vendor_cls = JuniperCommandWorker
        elif vendor == 'arista':
            vendor_cls = AristaCommandWorker
        else:
            log.exception(f'invalid or unsupported network device vendor: "{vendor}"')
            success = False
            raw_samples = ERROR.UNSUPPORTED_VENBDOR
        if success:
            try:
                worker = vendor_cls(**con_params)
                raw_samples = worker.work(**con_params)
                log.debug(f'finished querying device {host}. response length: {len(raw_samples)}')
                dump = kwargs.get('dump')
                if dump:
                    log.debug(f'writing dump results to "{dump}"')
                    try:
                        lines = [_ for _ in raw_samples if _.strip()]
                        lines.insert(0, f"Time: {datetime.datetime.utcnow().strftime(_DEFAULTS['datetime_format'])} (local: {datetime.datetime.now().strftime(_DEFAULTS['datetime_format'])})")
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

    if success:
        try:
            log.debug('formatting results')
            if not isinstance(raw_samples, str):
                if isinstance(raw_samples, Iterable):
                    raw_samples = '\n'.join(raw_samples if isinstance(raw_samples, list) else [_ for _ in raw_samples])
            log.debug('results formatted')
        except Exception as ex:
            error = f'failed to format results: {str(ex)}'
            log.exception(error)
            success = False
            raw_samples = ERROR.FORMATTING

    if not success:
        error = raw_samples
        raw_samples = []
    else:
        error = None
    try:
        send_params = {k: v for k, v in kwargs.items() if k not in con_params}
        sent, msg = send_result(success=success, raw_samples=raw_samples, error=error, **send_params)
        if not sent:
            success, error = False, msg or f'failed to send message'
    except Exception as ex:
        error = f'failed to send results back: {str(ex)}'
        success = False

    log.debug(f'finished iteration. success: {success}. error: "{error}". len(samples string): {len(raw_samples)}')


def _parse_config(config, **kwargs):
    if not os.path.isfile(config):
        error = f'missing config file: {config}'
        log.error(error)
        raise ValueError(error)

    try:
        with open(config, 'r') as f:
            return json.load(f)
    except Exception as ex:
        log.exception(f'failed to parse config file: "{config}". error: "{str(ex)}"')
        raise ex


def _to_bool(x):
    if x is None:
        return None
    elif x in __BOOL_TYPES__:
        return x
    elif not isinstance(x, str):
        pass
    elif x.lower() == 'true':
        return True
    elif x.lower() == 'false':
        return False
    error = f'invalid bool: "{x}"'
    log.error(error)
    raise ValueError(error)


def _parse_vendor(vendor):
    if not vendor:
        return 'cisco'
    vendor = vendor.strip().lower()
    if vendor in ('cisco', 'juniper', 'arista'):
        return vendor

    error = f'invalid vendor: "{vendor}"'
    log.exception(error)
    raise ValueError(error)

def _parse_ip(ip, throw=False):
    try:
        ip = ipaddress.IPv4Address(ip)
        return str(ip)
    except Exception as ex:
        if throw:
            log.exception(f'failed to parse ip: "{ip}". error: {str(ex)}')
            raise ex
        return None

_types = {
    str: lambda x: x if isinstance(x, str) else str(x),
    int: lambda x: x if isinstance(x, int) else int(x),
    bool: _to_bool,
    'vendor': _parse_vendor,
    'ip': _parse_ip,
}

_conf_keys = {
    'config': str,
    'logfile': str,
    'verbose': bool,
    'dump': str,
    'to_stderr': bool,
    'to_stdout': bool,

    'identifier': str,
    'host': 'ip',
    'port': int,
    'vendor': 'vendor',
    'username': str,
    'password': str,
    'command_prefix': str,

    'url_scheme': str,
    'url_host': 'ip',
    'url_port': int,
    'url_path': str,
    'url_method': str,
}

def _parse_env_vars(args):
    args.update({
        _: os.environ.get(f'SECUNITY_{_.upper()}')
        for _ in ('config',
                  'logfile', 'verbose', 'dump', 'to_stderr', 'to_stdout',
                  'identifier',
                  'host', 'port', 'vendor', 'username', 'password', 'command_prefix',
                  'url_scheme', 'url_host', 'url_port', 'url_path', 'url_method',)
        if args.get(_) is None and os.environ.get(f'SECUNITY_{_.upper()}') is not None
    })

    return args


def _set_args_types(args, rm_keys=False):
    if rm_keys:
        _rm_keys = []
    for key, _type in _conf_keys.items():
        value = args.get(key)
        if value is not None:
            args[key] = _types[_type](value)
        elif rm_keys:
            _rm_keys.append(key)
    if rm_keys:
        for key in _rm_keys:
            args.pop(key, None)
    return args


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
    parser.add_argument('-n', '--vendor', type=str, default='cisco', help='The Vendor of the Router')
    parser.add_argument('-u', '--user', '--username', type=str, default=None, help='SSH user')
    parser.add_argument('-w', '--password', type=str, default=None, help='SSH password')
    parser.add_argument('-k', '--key_filename', type=str, default=None, help='SSH Key Filename')

    parser.add_argument('--command_prefix', type=str, default=None,
                        help='The prefix to use when sending commands to the Router using SSH (for instance "cli" in Juniper)')

    parser.add_argument('--url', type=str, help='The URL to use for remove server', default=None)
    parser.add_argument('--url_scheme', type=str, help='Remote server URL scheme', default=None)
    parser.add_argument('--url_host', type=str, help='Remote server URL hostname', default=None)
    parser.add_argument('--url_port', type=int, help='Remote server URL port', default=0)
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
