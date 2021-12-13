from common.api_secunity import send_result
from common.consts import ACTION_FLOW_STATUS,  COMMENT
from common.logs import Log
from common.utils import get_con_params
from router_command import  MikroTikApiCommandWorker


def remove_flows(outgoing_flows_to_remove, worker, **kwargs):
    raw_samples = worker.work(**kwargs)

    for outgoing_flow_id in outgoing_flows_to_remove:
        _id = next((flow.get('id') for flow in raw_samples if flow.get(COMMENT) == outgoing_flow_id), None)
        try:
            if _id is not None:
                worker.remove_flow_with_id(_id=_id)
        except Exception as ex:
            Log.error(f'failed to remove flow. flow: {outgoing_flow_id} .ex:{str(ex)}')

        try:
            suffix_url_path = f"flows/{ACTION_FLOW_STATUS.REMOVED}/{outgoing_flow_id}"
            sent, msg = send_result(suffix_url_path=suffix_url_path, **kwargs)
        except Exception as ex:
            Log.error(ex)


def add_flows(outgoing_flows_to_add, worker, **kwargs):
    for _ in outgoing_flows_to_add:
        try:
            worker.add_flow(flow_to_add=_)
        except Exception as ex:
            Log.error(f'failed to add flow. flow: {_.get(COMMENT)} .ex:{str(ex)}')

        try:
            suffix_url_path = f"flows/{ACTION_FLOW_STATUS.APPLIED}/{_.get(COMMENT)}"
            sent, msg = send_result(suffix_url_path=suffix_url_path, **kwargs)

        except Exception as ex:
            Log.error(ex)


def add_remove_flow_mikrotik(outgoing_flows_to_add, outgoing_flows_to_remove, worker=None, con_params=None, **kwargs):
    if worker is None:
        if con_params is None:
            success, error, con_params = get_con_params(**kwargs)
        worker = MikroTikApiCommandWorker(**con_params)

    if outgoing_flows_to_add:
        add_flows(outgoing_flows_to_add=outgoing_flows_to_add, worker=worker, **kwargs)

    if outgoing_flows_to_remove:
        remove_flows(outgoing_flows_to_remove=outgoing_flows_to_remove, worker=worker, **kwargs)
