import argparse
import copy
import os

from common.configs import load_env_settings, parse_config_file, _cnf, update_config_types
from common.consts import DEFAULTS, VENDOR, ARGS_DEFAULTS, SEND_RESULT_DEFAULTS
from common.logs import Log


def get_argarse(title: str = None, supervisor_path: str = True,
                config: bool = True, config_title: str = None,
                host: bool = True, host_title: str = None,
                port: bool = True, port_title: str = None,
                username: bool = True, username_title: str = None,
                password: bool = True, password_title: str = None,
                key_filename: bool = True, key_filename_title: str = None,
                command_prefix: bool = False, command_prefix_title: str = None,
                vendor: bool = True, default_vendor: VENDOR = None,
                dump: bool = False,
                dump_value: str = None, dump_title: str = None,
                log: bool = True,
                logfile_path_value: str = None, logfile_title: str = None,
                verbose_value: bool = None, verbose_title: str = None,
                to_stdout_value: bool = None, to_stdout_title: str = None,
                to_stderr_value: bool = None, to_stderr_title: str = None,
                url: bool = False,
                url_value: str = None, url_title: str = None,
                url_scheme_value: str = None, url_scheme_title: str = None,
                url_host_value: str = None, url_host_title: str = None,
                url_port_value: int = None, url_port_title: str = None,
                url_path_value: str = None, url_path_title: str = None,
                url_method_value: str = None, url_method_title: str = None,
                parse: bool = True) -> dict:
    if not title:
        title = ARGS_DEFAULTS['title']
    parser = argparse.ArgumentParser(description=title)

    if supervisor_path:
        if not config_title:
            config_title = ARGS_DEFAULTS['config_title']
        parser.add_argument('-sv', '--supervisor_path', type=str, help=config_title, default=DEFAULTS['supervisor_path'])

    if config:
        if not config_title:
            config_title = ARGS_DEFAULTS['config_title']
        parser.add_argument('-c', '--config', type=str, help=config_title, default=DEFAULTS['config'])

    parser.add_argument('--identifier', '--id', type=str, help='Device ID', default=None)

    if vendor:
        if not default_vendor:
            default_vendor = VENDOR.DEFAULT_VENDOR
        parser.add_argument('-n', '--vendor', type=str, default=default_vendor, help='The Vendor of the Router')

    if host:
        if not host_title:
            host_title = ARGS_DEFAULTS['host_title']
        parser.add_argument('-s', '--host', '--ip', type=str, help='Router IP', default=host_title)
    if port:
        if not port_title:
            port_title = ARGS_DEFAULTS['port_title']
        parser.add_argument('-p', '--port', type=int, default=None, help=port_title)

    if username:
        if not username_title:
            username_title = ARGS_DEFAULTS['username_title']
        parser.add_argument('-u', '--user', '--username', type=str, default=None, help=username_title)
    if password:
        if not password_title:
            password_title = ARGS_DEFAULTS['password_title']
        parser.add_argument('-w', '--password', type=str, default=None, help=password_title)
    if key_filename:
        if not key_filename_title:
            key_filename_title = ARGS_DEFAULTS['key_filename_title']
        parser.add_argument('-k', '--key_filename', type=str, default=None, help=key_filename_title)

    if command_prefix:
        if not command_prefix_title:
            command_prefix_title = ARGS_DEFAULTS['command_prefix_title']
        parser.add_argument('--command_prefix', type=str, default=None, help=command_prefix_title)

    if log:
        if not logfile_title:
            logfile_title = ARGS_DEFAULTS['logfile_title']
        if logfile_path_value is None:
            logfile_path_value = ARGS_DEFAULTS['logfile_path']
        parser.add_argument('-lp', '--logfile_path', type=str, help=logfile_title, default=logfile_path)

        if not verbose_title:
            verbose_title = ARGS_DEFAULTS['verbose_title']
        if verbose_value not in (True, False):
            verbose_value = ARGS_DEFAULTS['verbose']
        parser.add_argument('-v', '--verbose', type=bool, help=verbose_title, default=verbose_value)

        if not to_stdout_title:
            to_stdout_title = ARGS_DEFAULTS['to_stdout_title']
        if to_stdout_value not in (True, False):
            to_stdout_value = ARGS_DEFAULTS['to_stdout_value']
        parser.add_argument('--to_stdout', '--stdout', type=str, help=to_stdout_title, default=to_stdout_value)

        if not to_stderr_title:
            to_stderr_title = ARGS_DEFAULTS['to_stderr_title']
        if to_stderr_value not in (True, False):
            to_stderr_value = ARGS_DEFAULTS['to_stderr_value']
        parser.add_argument('--to_stderr', '--stderr', type=str, help=to_stderr_title, default=to_stderr_value)

    if dump:
        if not dump_title:
            dump_title = ARGS_DEFAULTS['dump_title']
        parser.add_argument('-d', '--dump', type=str, help=dump_title, default=dump_value)

    if url:
        if not url_title:
            url_title = ARGS_DEFAULTS['url_title']
        parser.add_argument('--url', type=str, help=url_title, default=url_value)

        if not url_scheme_title:
            url_scheme_value = ARGS_DEFAULTS['url_scheme_title']
        if not url_scheme_value:
            url_scheme_value = SEND_RESULT_DEFAULTS['url_scheme']
        parser.add_argument('--url_scheme', type=str, help=url_scheme_title, default=url_scheme_value)

        if not url_host_title:
            url_host_title = ARGS_DEFAULTS['url_host_title']
        if not url_host_value:
            url_host_value = SEND_RESULT_DEFAULTS['url_host']
        parser.add_argument('--url_host', type=str, help=url_host_title, default=url_host_value)

        if not url_port_title:
            url_port_title = ARGS_DEFAULTS['url_port_title']
        if not url_port_value:
            url_port_value = SEND_RESULT_DEFAULTS['url_port']
        parser.add_argument('--url_port', type=int, help=url_port_title, default=url_port_value)

        if not url_path_title:
            url_path_title = ARGS_DEFAULTS['url_path_title']
        if not url_path_value:
            url_path_value = SEND_RESULT_DEFAULTS['url_path']
        parser.add_argument('--url_path', type=str, help=url_path_title, default=url_path_value)

        if not url_method_title:
            url_method_title = ARGS_DEFAULTS['url_method']
        if not url_method_value:
            url_method_value = SEND_RESULT_DEFAULTS['url_method']
        parser.add_argument('--url_method', type=str, help=url_method_title, default=url_method_value)

    if not parse:
        return argparse

    args = parser.parse_args()
    args = vars(args)
    return args


def initialize_start(argsparse_params: dict,
                     module: str = None,
                     **kwargs):
    args = get_argarse(**argsparse_params)

    args = load_env_settings(args)
    config = args['config']
    if config:
        config = parse_config_file(config)
        if config:
            args.update(config)
    args = update_config_types(config=args)

    _cnf.clear()
    _cnf.update({k: v for k, v in copy.deepcopy(args).items()})
    Log.initialize(module=module, **args)
    return args
