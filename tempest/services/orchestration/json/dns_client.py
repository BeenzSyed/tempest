__author__ = 'sabe6191'

import json
import datetime

from tempest.common import rest_client


class DnsClient(rest_client.RestClient):

    def __init__(self, config, username, password, auth_url,
                 token_url ,tenant_name=None):
        super(DnsClient, self).__init__(config, username, password,
                                                  auth_url,token_url,
                                                  tenant_name)
        self.url = self.config.dns.url
        self.service = self.config.dns.catalog_type

    def list_domain_id(self, domain_id ,region):

        url = domain_id
        resp, body = self.get(url,region)
        if resp['status'] in('200','201'):
            body = json.loads(body)
        return resp, body

def datehandler(obj):
    if isinstance(obj, datetime.date):
        return str(obj)
    else:
        raise TypeError, 'Object of type %s with value of %s is not ' \
                         'JSON serializable' % (type(obj), repr(obj))