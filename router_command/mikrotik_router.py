import routeros_api
try: import jstyleson as json
except: import json
class MikroTikApiCommandWorker():
    def __init__(self, host, user='admin', password='', **kwargs):
        # gilad to handle empty password and for the db we have to fill some password
        if password == 'aa':
            password = '' \
                       ''
        self.connection = routeros_api.RouterOsApiPool(host, username=user, password=password)
        self.api = self.connection.get_api()

        self.outgoing_path= self.api.get_resource('/ip/firewall/filter')

    def work(self,  **kwargs):

        stats = self.get_stats_from_router(**kwargs)
        return stats

    def remove_all_flows(self,  **kwargs):
        flows = self.get_stats_from_router()
        for _ in flows:
            try:
                self.outgoing_path.remove(id=_.get('id'))
            except Exception as ex:
                print(ex)
    def get_stats_from_router(self,  **kwargs):
        outgoing_list = self.outgoing_path.get()
        outgoing_list = json.loads(json.dumps(outgoing_list))
        return outgoing_list

    def delete_flow(self, _id):
        _id = str(_id)
        outgoing_list = self.get_stats_from_router()
        flow_to_delete = next((_.get('id') for _ in outgoing_list if _.get('comment') == _id), None)
        if flow_to_delete:
            res = self.outgoing_path.remove(id=flow_to_delete)
            return res

    def remove_flow_with_id(self, _id):

        res = self.outgoing_path.remove(id=_id)
        return res

    def set_flow(self, flow_to_add: dict):
        res = self.outgoing_path.set(**flow_to_add)

    def add_flow(self, flow_to_add: dict):
        flow_to_add = {**flow_to_add,
                       'action': 'drop',
                    'chain': 'forward',
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
