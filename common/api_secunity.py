import datetime
import requests


from common.utils import log

_SEND_RESULT_DEFAULTS = {
    'url_scheme': 'https',
    'url_host': 'api.secunity.io',
    'url_port': '5000',
    'url_path': 'in',
    'url_method': 'POST'
}


def _parse_identifier(identifier=None, **kwargs):
    if not identifier:
        identifier = kwargs.get('device_identifier') or kwargs.get('device') or kwargs.get('key')
        kwargs['identifier'] = identifier
    return identifier


# todo need to debug and make it work properly
def get_default_url(suffix_url_path, identifier, **kwargs):
    url_params = {k: kwargs[k] if kwargs.get(k) or isinstance(kwargs.get(k), bool) else v
                  for k, v in _SEND_RESULT_DEFAULTS.items()}
    url_prefix = '{url_scheme}://{url_host}:{url_port}/{url_path}'.format(**url_params)
    url_path = f'{url_prefix}/{identifier}/{suffix_url_path}'

    return url_path


def send_result(suffix_url_path, success=True, error=None, data=None, **kwargs):
    log.debug('starting message sending')
    identifier = _parse_identifier(**kwargs)

    url_path = get_default_url(suffix_url_path=suffix_url_path,  **kwargs)


    log.debug(f'sending result for identifier {identifier} to {url_path}')

    method = kwargs.get('url_method') or _SEND_RESULT_DEFAULTS['url_method']
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
        return 200 <= response.status_code <= 210, response.json()
    except Exception as ex:
        return False, str(ex)
