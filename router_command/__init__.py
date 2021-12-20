from collections import Iterable

from common.utils import Log, get_con_params
from common.consts import VENDOR, ERROR

from router_command.mikrotik_router import MikroTikApiCommandWorker
from router_command.exabgp_router import CiscoCommandWorker, JuniperCommandWorker, AristaCommandWorker

def get_vendor_class(**kwargs):
    success = True

    vendor = kwargs['vendor'].strip().lower()
    host = kwargs['host']
    Log.debug(f'starting to query device "{host}", vendor: "{vendor}"')
    if vendor == VENDOR.CISCO:
        vendor_cls = CiscoCommandWorker
    elif vendor == VENDOR.MIKROTIK:
        vendor_cls = MikroTikApiCommandWorker
    elif vendor == VENDOR.JUNIPER:
        vendor_cls = JuniperCommandWorker
    elif vendor == VENDOR.ARISTA:
        vendor_cls = AristaCommandWorker
    else:
        Log.exception(f'invalid or unsupported network device vendor: "{vendor}"')
        success = False

    return success,  vendor_cls, vendor

def get_command_worker(**kwargs):
    success, error, con_params = get_con_params(**kwargs)

    if success:
        success, vendor_cls, vendor = get_vendor_class(**kwargs)
    if success:

        worker = vendor_cls(**con_params)
        return worker, con_params
    return False, False


def parse_raw_sample(raw_samples, vendor, **kwargs):
    try:
        Log.debug('formatting results')
        if not isinstance(raw_samples, str) and vendor != VENDOR.MIKROTIK:
            if isinstance(raw_samples, Iterable):
                raw_samples = '\n'.join(raw_samples if isinstance(raw_samples, list) else [_ for _ in raw_samples])
        Log.debug('results formatted')
        return raw_samples, None
    except Exception as ex:
        error = f'{ERROR.FORMATTING} failed to format results: {str(ex)}'
        Log.exception(error)
        return False, error
