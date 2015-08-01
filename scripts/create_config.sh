#!/bin/bash -e

usage="Usage: ./create_config -e ENVIRONMENT -a ACCOUNT

Required arguments.
  -e  Environment to create stack in.
  -a  Account to create stack in.

Examples:
./create_config -e dev -a managed
./create_config -e prod-lon -a unmanaged_uk
"

# Parse command-line options
while getopts "e:a:" opt; do
    case "$opt" in
        e)  environment=$OPTARG
            ;;
        a)  account=$OPTARG
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            exit 1
            ;;
    esac
done

if [[ $environment == "dev" ]]; then
    uri=https://api.dev.rs-heat.com/v1
    regions=Dev
elif [[ $environment == "dev-fusion" ]]; then
    uri=https://fusion.dev.rs-heat.com/v1
    regions=Dev
elif [[ $environment == "qa" ]]; then
    uri=https://api.qa.rs-heat.com/v1
    regions=QA
elif [[ $environment == "staging" ]]; then
    uri=https://api.staging.rs-heat.com/v1
    regions=Staging
elif [[ $environment == "inactive-staging" ]]; then
    uri=https://inactive.staging.rs-heat.com/v1
    regions=Staging
elif [[ $environment == "prod-dfw prod-iad prod-ord prod-syd prod-hkg" ]]; then
    uri=https://identity.api.rackspacecloud.com/v2.0/
    regions=DFW,IAD,ORD,SYD,HKG
elif [[ $environment == "prod-dfw" ]]; then
    uri=https://dfw.orchestration.api.rackspacecloud.com/v1
    regions=DFW
elif [[ $environment == "prod-iad" ]]; then
    uri=https://iad.orchestration.api.rackspacecloud.com/v1
    regions=IAD
elif [[ $environment == "prod-ord" ]]; then
    uri=https://ord.orchestration.api.rackspacecloud.com/v1
    regions=ORD
elif [[ $environment == "prod-syd" ]]; then
    uri=https://syd.orchestration.api.rackspacecloud.com/v1
    regions=SYD
elif [[ $environment == "prod-hkg" ]]; then
    uri=https://hkg.orchestration.api.rackspacecloud.com/v1
    regions=HKG
elif [[ $environment == "prod-lon" ]]; then
    uri=https://lon.orchestration.api.rackspacecloud.com/v1
    regions=LON
elif [[ $environment == "inactive-prod-dfw" ]]; then
    uri=https://inactive.dfw.orchestration.api.rackspacecloud.com/v1
    regions=DFW
elif [[ $environment == "inactive-prod-iad" ]]; then
    uri=https://inactive.iad.orchestration.api.rackspacecloud.com/v1
    regions=IAD
elif [[ $environment == "inactive-prod-ord" ]]; then
    uri=https://inactive.ord.orchestration.api.rackspacecloud.com/v1
    regions=ORD
elif [[ $environment == "inactive-prod-syd" ]]; then
    uri=https://inactive.syd.orchestration.api.rackspacecloud.com/v1
    regions=SYD
elif [[ $environment == "inactive-prod-hkg" ]]; then
    uri=https://inactive.hkg.orchestration.api.rackspacecloud.com/v1
    regions=HKG
elif [[ $environment == "inactive-prod-lon" ]]; then
    uri=https://inactive.lon.orchestration.api.rackspacecloud.com/v1
    regions=LON
elif [[ $environment == "inactive-prod-dfw inactive-prod-iad inactive-prod-ord inactive-prod-syd inactive-prod-hkg" ]]; then
    uri=https://inactive.dfw.orchestration.api.rackspacecloud.com/v1,https://inactive.iad.orchestration.api.rackspacecloud.com/v1,https://inactive.ord.orchestration.api.rackspacecloud.com/v1,https://inactive.syd.orchestration.api.rackspacecloud.com/v1,https://inactive.hkg.orchestration.api.rackspacecloud.com/v1,
    regions=DFW,IAD,ORD,SYD,HKG
fi

if [[ $account == "unmanaged" ]]; then
    username=heatqe2
    password=TS?+4SL@V@?fc9*#
    tenantid=883286
elif [[ $account == "managed" ]]; then
    username=heatqe
    password=4cC:{fs3\\^atP!KD
    tenantid=862456
elif [[ $account == "heatqe5" ]]; then
    username=heatqe5
    password=VjQPBU@JF4uf*u6M
    tenantid=960893
elif [[ $account == "managed_operations" ]]; then
    username=heatqemanop
    password=Panda789!
    tenantid=925273
elif [[ $account == "infrastructure" ]]; then
    username=heatqe6
    password=VjQPBU@JF4uf*u6M
    tenantid=960899
elif [[ $account == "managed_infrastructure" ]]; then
    username=heatqeman
    password=Panda789!
    tenantid=925272
elif [[ $account == "unmanaged_UK" ]]; then
    username=heatlon
    password=Panda789!
    tenantid=10036073
elif [[ $account == "managed_UK" ]]; then
    username=heatlonmanop
    password=Panda789!
    tenantid=10041694
elif [[ $account == "rackconnect_v3_dfw" ]]; then
    username=rcheatdfwv3
    password=Panda789!
    tenantid=935179
elif [[ $account == "heatdev" ]]; then
    username=heatdev
    password=U{B?ZJMe:8CVge4AL
    tenantid=836933
elif [[ $account == "admin" ]]; then
    username=heat.admin
    password=ryp6ivyKyhun
    tenantid=883286
elif [[ $account == "creator" ]]; then
    username=heat.creator
    password=edrucolful6I
    tenantid=883286
elif [[ $account == "observer" ]]; then
    username=heat.observer
    password=Nabrareant8r
    tenantid=883286
fi

cat > etc/test_config.conf << EOF

[identity]
# This section contains configuration options that a variety of Tempest
# test clients use when authenticating with different user/tenant
# combinations

# The type of endpoint for a Identity service. Unless you have a
# custom Keystone service catalog implementation, you probably want to leave
# this value as "identity"
catalog_type = identity
# Ignore SSL certificate validation failures? Use when in testing
# environments that have self-signed SSL certs.
disable_ssl_certificate_validation = True
# URL for where to find the OpenStack Identity API endpoint (Keystone)

uri = $uri
uri_token = https://identity.api.rackspacecloud.com/v2.0/
# URL for where to find the OpenStack V3 Identity API endpoint (Keystone)
# Should typically be left as keystone unless you have a non-Keystone
# authentication API service
strategy = keystone

# This should be the username of a user WITHOUT administrative privileges
username = ${username}
# The above non-administrative user's password
password = ${password}
# The above non-administrative user's tenant name
tenant_name = ${tenantid}


[orchestration]
# Status change wait interval
build_interval = 1

# Status change wait timout. This may vary across environments as some some
# tests spawn full VMs, which could be slow if the test is already in a VM.
build_timeout = 1800

# Whether or not Heat is expected to be available
heat_available = true

# Instance type for tests. Needs to be big enough for a
# full OS plus the test workload
instance_type = m1.micro

# Name of heat-cfntools enabled image to use when launching test instances
# If not specified, tests that spawn instances will not run
image_ref = ubuntu-vm-heat-cfntools

# Name of existing keypair to launch servers with. The default is not to specify
# any key, which will generate a keypair for each test class

key_name = sabeen
env = ${environment}
regions = ${regions}


[service_available]
# Whether or not cinder is expected to be available
cinder = True
# Whether or not neutron is expected to be available
neutron = false
# Whether or not glance is expected to be available
glance = True
# Whether or not swift is expected to be available
swift = True
# Whether or not nova is expected to be available
nova = True
# Whether or not Heat is expected to be available
heat = True
# Whether or not horizon is expected to be available
horizon = True

EOF
