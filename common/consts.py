
import pytz

try:
    import paramiko
    __SSH_PORT__ = paramiko.config.SSH_PORT
except:
    __SSH_PORT__ = 22

SECUNITY = 'SECUNITY'
COMMENT = 'comment'


SSH_DEFAULTS = {
    'port': __SSH_PORT__,
    'warn': False,
    'pty': True,
    'timeout': 30
}
class ACTION_FLOW_STATUS():
    APPLIED = 'applied'
    REMOVED = 'removed'

class HEALTH_CHECK():
    MAX_SIZE_LOG = 10
    MIN_SIZE_LOG = MAX_SIZE_LOG // 2
    SYNC_CAUSE_NO_HEALTH_FOR_LONG_TIME = 60 * 1212
    FORMAT_TIME = '%Y-%m-%d - %H:%M:%S'


SCHEDULER_SETTINGS = {
    'start': True,
    'executor_threadpool_size': 30,
    'timezone': 'UTC',
}

class VENDOR:
    CISCO = 'cisco'
    JUNIPER = 'juniper'
    ARISTA = 'arista'
    MIKROTIK = 'mikrotik'

    DEFAULT_VENDOR = CISCO

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

class ERROR:
    CONERROR = 'conerror'
    INVALID_CON_PARAMS = 'invalid-con-params'
    UNSUPPORTED_VENBDOR = 'unsupported-vendor'
    FORMATTING = 'formatting'

    __ALL__ = (CONERROR, INVALID_CON_PARAMS, UNSUPPORTED_VENBDOR, FORMATTING)

    @classmethod
    def has(cls, value):
        return value in cls.__ALL__

ok_health_check_file_path = "logs/ok_health_check.txt"
error_health_check_file_path = "logs/error_health_check.txt"
DEFAULTS = {
    'config': '/etc/secunity/secunity.conf',
    'datetime_format': '%Y-%m-%d %H:%M:%S',
    'supervisor_path': "/etc/supervisor/supervisord.conf",
    'logfile_module': SECUNITY.lower(),
    'ok_health_check_file_name': 'ok_health_check.txt',
    'error_health_check_file_name': 'error_health_check.txt',

    # 'logfile_module': "/var/log/secunity/"

}
DEBUG_GILAD = True
if DEBUG_GILAD:
    DEFAULTS['config'] = 'logs/local.conf'

SEND_RESULT_DEFAULTS = {
    'url_scheme': 'https',
    'url_host': 'api.secunity.io',
    'url_port': 443,
    'url_path': 'in',
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
ARGS_DEFAULTS = {
    'title': 'Secunity\'s On-Prem Agent',
    'config_title': 'Config file full file path, overriding all other options',
    'host_title': 'Router IP Address',
    'ok_health_check_title': 'Log dates of good connection with secunity to file txt',
    'error_health_check_title': 'Log dates of bad connection with secunity to file txt',
    'port_title': 'Router Connect Port',
    'username_title': 'Router Connect User',
    'password_title': 'Router Connect Password',
    'key_filename_title': 'Router Connect Key Filename',
    'command_prefix_title': 'The prefix to wrap commands sent to the Router (for instance "cli" in Juniper)',
    'logfile_path':  "/var/log/secunity",
    'logfile_title': 'Full file path to log to',
    'verbose': True,
    'verbose_title': 'Indicates whether to log verbose data',
    'to_stdout_title': 'Log messages to stdout',
    'to_stdout_value': True,
    'to_stderr_title': 'Log errors to stderr',
    'to_stderr_value': False,
    'dump_title': 'Full file path to dump results',
    'url_title': 'Secunity\'s API URL',
    'url_scheme_title': 'Secunity\'s API URL scheme (http/https)',
    'url_host_title': 'Secunity\'s API URL host',
    'url_port_title': 'Secunity\'s API URL port',
    'url_path_title': 'Secunity\'s API URL path',
    'url_method_title': 'Secunity\'s API HTTP method',
    'url_method': 'POST',
    'comment_flow_prefix': SECUNITY,
    'comment_flow_prefix_title': 'Prefix in comment for flow Secunity\'s will add',

}