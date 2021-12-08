from common.utils import Log, VENDOR

# router_command_type should be in the environment like os.get
router_command_type : VENDOR = VENDOR.CISCO

if router_command_type == VENDOR.MIKROTIK:
    from router_command.mikrotik_router import MikroTikApiCommandWorker
else:
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
