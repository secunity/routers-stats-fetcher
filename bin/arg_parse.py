import argparse
import time
import copy
import os

from common.configs import load_env_settings, _parse_config, _cnf, get_log_settings, update_config_types
from common.consts import DEFAULTS
from common.logs import log
# from common.utils import _set_args_types


def get_argarse(config: bool = True,
                debug: bool = False,
                log: bool = True,
                url: bool = False,
                parse: bool = True):
    parser = argparse.ArgumentParser(description='Secunity On-Prem Agent')
    if config:
        parser.add_argument('-c', '--config', type=str, help='Config file (overriding all other options)',
                            default=DEFAULTS['config'])

    parser.add_argument('--identifier', '--id', type=str, help='Device ID', default=None)

    parser.add_argument('-s', '--host', '--ip', type=str, help='Router IP', default=None)
    parser.add_argument('-p', '--port', type=int, default=None, help='SSH port')
    parser.add_argument('-n', '--vendor', type=str, default='mikrotik', help='The Vendor of the Router')
    parser.add_argument('-u', '--user', '--username', type=str, default=None, help='SSH user')
    parser.add_argument('-w', '--password', type=str, default=None, help='SSH password')
    parser.add_argument('-k', '--key_filename', type=str, default=None, help='SSH Key Filename')

    parser.add_argument('--command_prefix', type=str, default=None,
                        help='The prefix to use when sending commands to the Router using SSH (for instance "cli" in Juniper)')

    if log:
        parser.add_argument('-l', '--logfile', type=str, help='File to log to', default=None)
        parser.add_argument('-v', '--verbose', type=bool, help='Indicates whether to log verbose data', default=True)
        parser.add_argument('--to_stdout', '--stdout', type=str, help='Log messages to stdout', default=True)
        parser.add_argument('--to_stderr', '--stderr', type=str, help='')

    if debug:
        parser.add_argument('-d', '--dump', type=str, help='File path to dump results')

    if url:
        parser.add_argument('--url', type=str, help='The URL to use for remove server', default=None)
        parser.add_argument('--url_scheme', type=str, help='Remote server URL scheme', default=None)
        parser.add_argument('--url_host', type=str, help='Remote server URL hostname', default=None)
        parser.add_argument('--url_port', type=int, help='Remote server URL port', default=0)
        parser.add_argument('--url_path', type=str, help='Remote server URL path', default=None)
        parser.add_argument('--url_method', type=str, help='Remote server URL method', default=None)

    if not parse:
        return argparse

    args = parser.parse_args()
    args = vars(args)
    return args

def initialize_start():


    args = get_argarse()
    args = load_env_settings(args)
    config = args['config']
    if config:
        config = _parse_config(config)
        args.update(config)
    args = update_config_types(config=args)

    #todo add pwd_logfile for using current path
    if args.get('logfile'):
        args['logfile'] = f"{os.getcwd()}/{args.get('logfile')}"
    _cnf.update({k: v for k, v in copy.deepcopy(args).items()})
    log.initialize(**args)
    return args