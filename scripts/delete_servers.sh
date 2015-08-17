from novaclient import client as nc
from novaclient import exceptions as ex
import argparse

parser = argparse.ArgumentParser(description='Delete Novaclient Servers.')
parser.add_argument('username', help='Identity username.')
parser.add_argument('password', help='Identity password or API key.')
parser.add_argument('tenant_name', help='Identity tenant name.')
parser.add_argument('--dry-run', action='store_true', dest='dry_run',
                    help='Print what would be deleted.')
parser.add_argument('--verbose', action='store_true', dest='verbose',
                    help='Print deletion messages.')
parser.add_argument('--region', default='DFW', help='Region name.')
args = parser.parse_args()

NOVACLIENT_VERSION = '2'

client_args = {
    'project_id': args.tenant_name,
    'auth_url': 'https://identity.api.rackspacecloud.com/v2.0/',
    'username': args.username,
    'api_key': args.password,
    'region_name': args.region,
}

client = nc.Client(NOVACLIENT_VERSION, **client_args)

server_list = client.servers.list()

for each_server in server_list:
    if each_server.status == "DELETED" \
            or getattr(each_server, 'OS-EXT-STS:task_state') == "deleting":
        if args.dry_run:
            print '{0}'.format(each_server.name)
            continue
        if args.verbose:
            print 'Deleting {0}'.format(each_server.name)
        try:
            client.servers.delete(each_server)
        except ex.NotFound, e:
            print e
