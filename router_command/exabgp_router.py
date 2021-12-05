from abc import abstractmethod, ABC
import json

import paramiko
SSH_DEFAULTS = {
    'port': 22,
    'warn': False,
    'pty': True,
    'timeout': 30
}



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
# anyway command prefix will be None
# _cnf = {'__log_init__': False}
class JuniperCommandWorker(CommandWorker):

    def get_stats_from_router(self, credentials, **kwargs):
        command = 'show firewall filter detail __flowspec_default_inet__'
        # command_prefix = _cnf.get('command_prefix')
        # if command_prefix:
        #     if isinstance(command_prefix, str):
        #         command = f'{command_prefix} {command}'
        #     elif isinstance(command_prefix, bool) or command_prefix == 1:
        #         command = f'cli {command}'
        result = self.perform_cli_command(credentials=credentials, command=command, **kwargs)
        return result


class AristaCommandWorker(CommandWorker):

    def get_stats_from_router(self, credentials, **kwargs):
        command = 'sh flow-spec ipv4'
        result = self.perform_cli_command(credentials=credentials, command=command, **kwargs)
        return result
