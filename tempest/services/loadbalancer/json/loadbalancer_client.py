import json

from tempest.common.rest_client import RestClient


class Loadbalancerclient(RestClient):
    def __init__(self,
                 config,
                 username,
                 password,
                 auth_url,token_url,
                 tenant_name=None):
        super(Loadbalancerclient, self).__init__(config,
                                             username,
                                             password,
                                             auth_url,token_url,
                                             tenant_name)
        self.service = self.config.database.catalog_type

    def get_load_balancer(self, load_balancer_id,region):

        url = "loadbalancers/%s" %load_balancer_id
        resp, body = self.get(url, region)
        if resp['status']=='200':
             body = json.loads(body)
        return resp ,body