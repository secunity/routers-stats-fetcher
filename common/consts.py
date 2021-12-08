import pytz

try:
    import paramiko
    __SSH_PORT__ = paramiko.config.SSH_PORT
except:
    __SSH_PORT__ = 22


SSH_DEFAULTS = {
    'port': __SSH_PORT__,
    'warn': False,
    'pty': True,
    'timeout': 30
}
class ACTION_FLOW_STATUS():
    APPLIED = 'applied'
    REMOVED = 'removed'



class VENDOR:
    CISCO = 'cisco'
    JUNIPER = 'juniper'
    ARISTA = 'arista'
    MIKROTIK = 'mikrotik'

    DEFAULT_TYPE = CISCO

    __mapping__ = {
        'CISCO': CISCO,
        'JUNIPER': JUNIPER,
        'ARISTA': ARISTA,
        'MIKROTIK': MIKROTIK,
    }

    @classmethod
    def parse(cls, vendor: str):
        result = next((_ for _ in cls.__mapping__.values() if _ == vendor), None)
        if not result:
            result = next((_ for _ in cls.__mapping__.keys() if _ == vendor), None)
            if not result:
                raise ValueError(f'invalid vendor: "{str(vendor)}"')


DEFAULTS = {
    'config': 'routers-stats-fetcher.conf',
    'datetime_format': '%Y-%m-%d %H:%M:%S',
}


SEND_RESULT_DEFAULTS = {
    'url_host': 'api.secunity.io',
    'url_scheme': 'https',
    'url_path': 'fstats1/v1.0.0/in',
    'url_method': 'POST'
}


BOOL_TYPES = (True, False,)


ENV_PREFIX = 'SECUNITY_'


CONFIG_KEYS = {
    'config': str,
    'logfile': str,
    'verbose': bool,
    'dump': str,
    'to_stderr': bool,
    'to_stdout': bool,

    'identifier': str,
    'host': 'ip',
    'port': int,
    'vendor': str,
    'username': str,
    'password': str,
    'command_prefix': str,

    'url_scheme': str,
    'url_host': 'ip',
    'url_port': int,
    'url_path': str,
    'url_method': str,
}


class ERROR:
    CONNECTION_ERROR = 'connection_error'
    INVALID_CONNECTION_PARAMS = 'invalid_connection_params'
    UNSUPPORTED_VENDOR = 'unsupported_vendor'
    FORMATTING = 'formatting'

    __ALL__ = (CONNECTION_ERROR, INVALID_CONNECTION_PARAMS, UNSUPPORTED_VENDOR, FORMATTING)

    @classmethod
    def has(cls, value):
        return value in cls.__ALL__


LOG_CONFIG_KEYS = ('logfile', 'verbose', 'to_stdout', 'to_stderr')

SCHEDULER_CONFIG_KEYS = ('thread_pool_executor_size', 'timezone')

SCHEDULER_CONFIG_KEYS_DEFAULTS = {
    'thread_pool_executor_size': 30,
    'timezone': pytz.UTC
}
