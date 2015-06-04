__author__ = 'sabe6191'

from tempest.common import rest_client


class SwiftClient(rest_client.RestClient):

    def __init__(self, config, username, password, auth_url,
                 token_url, tenant_name=None):
        super(SwiftClient, self).__init__(config, username, password,
                                           auth_url, token_url, tenant_name)

    def list_swift_object(self, storage_id, region):
        url = "https://storage101.dfw1.clouddrive.com/v1/MossoCloudFS_%s" \
              % storage_id
        resp, body = self.get(url, region)
        return resp, body

    def list_auth_swift_object(self, storage_id, region):
        headers = dict(self.headers)
        headers['X-Auth-User'] = self.user
        headers['X-Auth-Token'] = self.token
        body = {}
        url = "https://storage101.dfw1.clouddrive.com/v1/MossoCloudFS_%s" \
              % storage_id
        resp, body = self.post(url=url, region=region, headers=headers, body=body)
        return resp, body
