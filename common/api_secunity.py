import datetime
import os
import requests
from requests.exceptions import ConnectionError

from common.consts import SEND_RESULT_DEFAULTS
from common.health_check import add_line, format_time, after_request, health_check_file_path, \
    error_health_check_file_path
from common.utils import Log


def _parse_identifier(identifier=None, **kwargs):
    if not identifier:
        identifier = kwargs.get('device_identifier') or kwargs.get('device') or kwargs.get('key')
        kwargs['identifier'] = identifier
    return identifier


def get_default_url(suffix_url_path, identifier, **kwargs):
    url_params = {k: kwargs[k] if kwargs.get(k) or isinstance(kwargs.get(k), bool) else v
                  for k, v in SEND_RESULT_DEFAULTS.items()}
    url_prefix = '{url_scheme}://{url_host}:{url_port}/{url_path}'.format(**url_params)
    url_path = f'{url_prefix}/{identifier}/{suffix_url_path}'

    return url_path


def send_result(suffix_url_path, success=True, error=None, worker=None, data={}, **kwargs):
    Log.debug('starting message sending')
    identifier = _parse_identifier(**kwargs)

    url_path = get_default_url(suffix_url_path=suffix_url_path,  **kwargs)


    Log.debug(f'sending result for identifier {identifier} to {url_path}')


    method = kwargs.get('url_method') or SEND_RESULT_DEFAULTS['url_method']
    func = getattr(requests, method.lower())
    try:
        if method == 'GET':
            response = func(url=url_path)
        else:
            result = {
                **data,
                'success': success,
                'error': error,
                'time': datetime.datetime.utcnow().isoformat()
            }
            response = func(url=url_path, json=result)
            if response.status_code == 500:
                if worker is not None and worker.__class__.__name__ == 'MikroTikApiCommandWorker':
                    worker.remove_all_flows()
            success = 200 <= response.status_code <= 210
        # return success, response.json() if success else response.text
    except ConnectionError as ex:
        if 'send_statistics' != suffix_url_path:
            error = 'remove_all_flow'

    except Exception as ex:
        Log.exception(str(ex))
        error = f'url_path: {url_path}'

    else:
        if success:
            after_request(url_path=url_path, file_path=health_check_file_path)
            return success, response.json()
        else:
            after_request(url_path=url_path, file_path=error_health_check_file_path)
            return success, response.text
    finally:
        after_request(url_path=url_path, file_path=error_health_check_file_path)
        return False, error
