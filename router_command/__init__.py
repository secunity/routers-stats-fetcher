from common.utils import Log, ERROR
from router_command.exabgp_router import CiscoCommandWorker, JuniperCommandWorker, AristaCommandWorker
from router_command.mikrotik_router import MikroTikApiCommandWorker


def get_vendor_class(**kwargs):
    success = True

    vendor = kwargs['vendor'].strip().lower()
    host = kwargs['host']
    Log.debug(f'starting to query device "{host}", vendor: "{vendor}"')
    if vendor == 'cisco':
        vendor_cls = CiscoCommandWorker
    elif vendor == 'mikrotik':
        vendor_cls = MikroTikApiCommandWorker
    elif vendor == 'juniper':
        vendor_cls = JuniperCommandWorker
    elif vendor == 'arista':
        vendor_cls = AristaCommandWorker
    else:
        Log.exception(f'invalid or unsupported network device vendor: "{vendor}"')
        success = False

    return success,  vendor_cls, vendor
