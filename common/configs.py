import copy
import os

from common.logs import log

try:
    import jstyleson as json
except:
    import json
from common.consts import ENV_PREFIX, CONFIG_KEYS, VENDOR, BOOL_TYPES, LOG_CONFIG_KEYS, SCHEDULER_CONFIG_KEYS, \
    SCHEDULER_CONFIG_KEYS_DEFAULTS

_cnf = {}

__CLONE_CONFIG_REQUEST__ = True


def _parse_clone(clone: bool = None):
    if clone is None:
        clone = __CLONE_CONFIG_REQUEST__
    elif clone not in BOOL_TYPES:
        raise ValueError('clone must be of type bool')
    return clone


def set_conf(config: dict,
             replace: bool = None,
             clone: bool = None
             ) -> dict:
    clone = _parse_clone(clone)

    if replace is None:
        replace = False
    elif replace not in BOOL_TYPES:
        raise ValueError('replace is not of type bool')

    global _cnf
    if replace:
        _cnf = copy.deepcopy(config)
    else:
        _cnf.update(config)

    return copy.deepcopy(_cnf) if clone else _cnf


def cnf_get(key: str,
            default: object = None,
            clone: bool = None) -> object:
    clone = _parse_clone(clone)

    value = _cnf.get(key, default=default)
    return copy.deepcopy(value) if clone else value


def load_env_settings(args: dict) -> dict:
    update = {
        _: os.environ.get(f'{ENV_PREFIX}{_.upper()}')
        for _ in CONFIG_KEYS.keys()
        if args.get(_) is None and os.environ.get(f'{ENV_PREFIX}{_.upper()}') is not None
    }
    if update:
        args.update(update)
    return args


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


_type_parse_methods = {
    'ip': None,
    'bool': None,
}


def parse_bool(*args, **kwargs):
    if not _type_parse_methods['bool']:
        from common.utils import parse_bool
        _type_parse_methods['bool'] = parse_bool
    return _type_parse_methods['bool'](*args, **kwargs)


def parse_ip(*args, **kwargs):
    if not _type_parse_methods['ip']:
        from common.utils import parse_ip
        _type_parse_methods['ip'] = parse_ip
    return _type_parse_methods['ip'](*args, **kwargs)


_config_types_mutation = {
    str: lambda x: x.strip(' \r\n\t') if isinstance(x, str) else str(x),
    int: lambda x: x if isinstance(x, int) else int(x.strip(' \r\n\t') if isinstance(x, str) else x),
    bool: parse_bool,
    'vendor': VENDOR.parse,
    'ip': parse_ip,
}
# def _set_args_types(args, rm_keys=False):
#     if rm_keys:
#         _rm_keys = []
#     for key, _type in CONFIG_KEYS.items():
#         value = args.get(key)
#         if value is not None:
#             mutation = _config_types_mutation.get(_type)
#             if mutation:
#                 config[key] = mutation(value)
#             args[key] = _types[_type](value)
#         elif rm_keys:
#             _rm_keys.append(key)
#     if rm_keys:
#         for key in _rm_keys:
#             args.pop(key, None)
#     return args


def update_config_types(config: dict,
                        rm_keys: bool = False,
                        clone: bool = None):
    clone = _parse_clone(clone)

    _rm_keys = []
    for key, _type in CONFIG_KEYS.items():
        value = config.get(key)
        if value is not None:
            mutation = _config_types_mutation.get(_type)
            if mutation:
                config[key] = mutation(value)
        elif rm_keys:
            _rm_keys.append(key)

    for key in _rm_keys:
        config.pop(key, None)

    return copy.deepcopy(config) if clone else config


def get_log_settings(config: dict = None,
                     clone: bool = None) -> dict:
    clone = _parse_clone(clone)
    if not config:
        config = _cnf

    value = {k: config.get(k) for k in LOG_CONFIG_KEYS}
    return copy.deepcopy(value) if clone else value


def get_scheduler_settings(config: dict = None,
                           clone: bool = None) -> dict:
    clone = _parse_clone(clone)
    if not config:
        config = _cnf
    result = {}
    for key in SCHEDULER_CONFIG_KEYS:
        value = config.get(key)
        if value is None:
            value = SCHEDULER_CONFIG_KEYS_DEFAULTS[key]
        result[key] = copy.deepcopy(value) if clone else value

    return result


