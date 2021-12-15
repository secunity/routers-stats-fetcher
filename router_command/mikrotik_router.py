import collections

import routeros_api

from common.consts import SECUNITY, COMMENT
from router_command.exabgp_router import CommandWorker

try:
    import jstyleson as json
except:
    import json
find_duplicate = lambda lst: [item for item, count in collections.Counter(lst).items() if count > 1]


class MikroTikApiCommandWorker(CommandWorker):
    def __init__(self, host: str, user: str, password: str, **kwargs):

        self.connection = routeros_api.RouterOsApiPool(host=host, username=user, password=password)
        self.api = self.connection.get_api()

        self.outgoing_path = self.api.get_resource('/ip/firewall/filter')

    def work(self, **kwargs):

        stats = self.get_stats_from_router(**kwargs)
        return stats

    def remove_all_flows(self, **kwargs):
        flows = self.get_stats_from_router()
        for _ in flows:
            try:
                self.remove_flow_with_id(id=_.get('id'))
            except Exception as ex:
                print(ex)


    def remove_duplicate(self, outgoing_comments, outgoing_list):
        to_remove = find_duplicate(outgoing_comments)
        while to_remove:
            index = outgoing_comments.index(to_remove.pop())
            outgoing_comments.pop(index)
            flow_mikro = outgoing_list.pop(index)
            _id_mikro = flow_mikro.get('id')
            self.remove_flow_with_id(_id=_id_mikro)

            if not to_remove:
                to_remove = find_duplicate(outgoing_comments)
        return outgoing_list
    def get_stats_from_router(self, comment_flow_prefix: str, only_secunity_flows: bool = True, **kwargs):
        outgoing_list = self.outgoing_path.get()
        outgoing_list = json.loads(json.dumps(outgoing_list))
        if only_secunity_flows:
            outgoing_list = [{ **flow, COMMENT: flow.get(COMMENT).split('_')[1]}
                             for flow in outgoing_list if comment_flow_prefix in flow.get(COMMENT, '')]

            outgoing_comments = [flow.get(COMMENT) for flow in outgoing_list]
            outgoing_list = self.remove_duplicate(outgoing_comments=outgoing_comments, outgoing_list=outgoing_list)
        return outgoing_list


    def remove_flow_with_id(self, _id):

        res = self.outgoing_path.remove(id=_id)
        return res

    def set_flow(self, flow_to_add: dict):
        res = self.outgoing_path.set(**flow_to_add)

    def add_flow(self, flow_to_add: dict, comment_flow_prefix: str, **kwargs):
        flow_to_add = {key: str(value) for key, value in flow_to_add.items()}
        flow_to_add['protocol'] = flow_to_add['protocol'].lower()
        flow_to_add[COMMENT] = f'{comment_flow_prefix}_{flow_to_add[COMMENT]}'

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
