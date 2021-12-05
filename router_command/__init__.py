from common.utils import log, ERROR
from router_command.exabgp_router import CiscoCommandWorker, JuniperCommandWorker, AristaCommandWorker
from router_command.mikrotik_router import MikroTikApiCommandWorker


def get_vendor_class(**kwargs):
    success, raw_samples = True, []

    vendor = kwargs['vendor'].strip().lower()
    host = kwargs['host']
    log.debug(f'starting to query device "{host}", vendor: "{vendor}"')
    if vendor == 'cisco':
        vendor_cls = CiscoCommandWorker
    elif vendor == 'mikrotik':
        vendor_cls = MikroTikApiCommandWorker
    elif vendor == 'juniper':
        vendor_cls = JuniperCommandWorker
    elif vendor == 'arista':
        vendor_cls = AristaCommandWorker
    else:
        log.exception(f'invalid or unsupported network device vendor: "{vendor}"')
        success = False
        raw_samples = ERROR.UNSUPPORTED_VENBDOR

    return success, raw_samples, vendor_cls, vendor
