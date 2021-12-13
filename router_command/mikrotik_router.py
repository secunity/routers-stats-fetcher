import routeros_api

from common.consts import SECUNITY, COMMENT
from router_command.exabgp_router import CommandWorker

try:
    import jstyleson as json
except:
    import json


class MikroTikApiCommandWorker(CommandWorker):
    def __init__(self, host, user='admin', password='', **kwargs):

        self.connection = routeros_api.RouterOsApiPool(host, username=user, password=password)
        self.api = self.connection.get_api()

        self.outgoing_path = self.api.get_resource('/ip/firewall/filter')

    def work(self, **kwargs):

        stats = self.get_stats_from_router(**kwargs)
        return stats

    def remove_all_flows(self, **kwargs):
        flows = self.get_stats_from_router()
        for _ in flows:
            try:
                self.outgoing_path.remove(id=_.get('id'))
            except Exception as ex:
                print(ex)

    def get_stats_from_router(self, only_secunity_flows: bool = True, **kwargs):
        outgoing_list = self.outgoing_path.get()
        outgoing_list = json.loads(json.dumps(outgoing_list))
        if only_secunity_flows:
            outgoing_list = [{ **flow, COMMENT: flow.get(COMMENT, 'n_o').split('_')[1]}
                             for flow in outgoing_list if SECUNITY in flow.get(COMMENT, '')]

        return outgoing_list

    def delete_flow(self, _id):
        _id = str(_id)
        outgoing_list = self.get_stats_from_router()
        flow_to_delete = next((_.get('id') for _ in outgoing_list if _.get(COMMENT) == _id), None)
        if flow_to_delete:
            res = self.outgoing_path.remove(id=flow_to_delete)
            return res

    def remove_flow_with_id(self, _id):

        res = self.outgoing_path.remove(id=_id)
        return res

    def set_flow(self, flow_to_add: dict):
        res = self.outgoing_path.set(**flow_to_add)

    def add_flow(self, flow_to_add: dict):
        flow_to_add = {key: str(value) for key, value in flow_to_add.items()}
        flow_to_add['protocol'] = flow_to_add['protocol'].lower()
        src_address = flow_to_add.get('src-address')
        if src_address and 'None' in src_address:
            del flow_to_add['src-address']
        flow_to_add = {**flow_to_add,
                       'action': 'drop',
                       'disabled': 'false',

                       }
        res = self.outgoing_path.add(**flow_to_add)


if __name__ == '__main__':
    a = MikroTikApiCommandWorker("172.20.1.10")
    # flow = {
    #     'action': 'drop',
    #     'chain': 'forward',
    #     'comment': '61a8e17381ffcc800a04aed9',
    #     'disabled': 'false',
    #     'dst-address': '185.144.88.19/32',
    #     'dst-port': '600',
    #     'packet-size': '260',
    #     'protocol': 'tcp',
    #     'src-address': '192.168.11.2/32'}
    # try:
    #     a.add_flow(flow)
    # except Exception as ex:
    #     print(ex)
