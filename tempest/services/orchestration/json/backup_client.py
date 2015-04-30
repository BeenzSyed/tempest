__author__ = 'sabe6191'

from tempest.common import rest_client


class BackupClient(rest_client.RestClient):

    def __init__(self, config, username, password, auth_url,
                 token_url, tenant_name=None):
        super(BackupClient, self).__init__(config, username, password,
                                           auth_url, token_url, tenant_name)

    def list_backup_config(self, agent_id, region):
        url = "https://dfw.backup.api.rackspacecloud.com/v1.0/%s/" \
              "backup-configuration/system/%s" % (self.tenant_name, agent_id)
        resp, body = self.get(url, region)
        return resp, body
