import datetime
import ipaddress
import sys
import logging
import requests
import os
import json
# _SEND_RESULT_DEFAULTS = {
#     'url_host': 'api.secunity.io',
#     'url_scheme': 'https',
#     'url_path': 'fstats1/v1.0.0/in',
#     'url_method': 'POST'
# }

_SEND_RESULT_DEFAULTS = {
    'url_host': '172.20.0.201',
    'url_scheme': 'http',
    'url_path': 'fstats1/v1.0.0/in',
    'url_method': 'POST'
}

_DEFAULTS = {
    'config': 'routers-stats-fetcher.conf',
    # 'config': '/opt/routers-stats-fetcher/routers-stats-fetcher.conf',
    'datetime_format': '%Y-%m-%d %H:%M:%S',
}


__BOOL_TYPES__ = (True, False,)

_cnf = {'__log_init__': False}

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




class ERROR:
    CONERROR = 'conerror'
    INVALID_CON_PARAMS = 'invalid-con-params'
    UNSUPPORTED_VENBDOR = 'unsupported-vendor'
    FORMATTING = 'formatting'

    __ALL__ = (CONERROR, INVALID_CON_PARAMS, UNSUPPORTED_VENBDOR, FORMATTING)

    @classmethod
    def has(cls, value):
        return value in cls.__ALL__

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
    if vendor in ('cisco', 'juniper', 'arista', 'mikrotik'):
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

