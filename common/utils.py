import ipaddress

from common.consts import BOOL_TYPES
from common.logs import Log

__BOOL_TYPES__ = (True, False,)

_cnf = {'__log_init__': False}



def get_con_params(**kwargs):
    try:
        success, error = True, None

        con_params = {
            k: v for k, v in kwargs.items()
            if not k.startswith('url') and k not in ('identifier', 'logfile_path', 'ok_health_check', 'error_health_check')
        }
    except Exception as ex:
        error = f'failed to parse connection params: {str(ex)}'
        Log.exception(error)
        success = False
    return success, error, con_params

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
    Log.error(error)
    raise ValueError(error)


def _parse_vendor(vendor):
    if not vendor:
        return 'cisco'
    vendor = vendor.strip().lower()
    if vendor in ('cisco', 'juniper', 'arista', 'mikrotik'):
        return vendor

    error = f'invalid vendor: "{vendor}"'
    Log.exception(error)
    raise ValueError(error)


def parse_bool(x: object, parse_str:dict =  False):
    if x is None:
        return None
    elif x in BOOL_TYPES:
        return x
    elif parse_str and isinstance(x, str):
        x = x.strip(' \r\n\t')
        if x.lower() == 'true':
            return True
        elif x.lower() == 'false':
            return False
    error = f'invalid bool: "{x}"'
    raise ValueError(error)


def parse_ip(ip, throw=False):
    try:
        ip = ipaddress.IPv4Address(ip)
        return str(ip)
    except Exception as ex:
        if throw:
            raise ex
        return None

