#!/bin/bash -e

export PYTHONUNBUFFERED=1

if [ ! -d ".env" ]; then
    echo "creating virtualenv"
    virtualenv .env
fi

source .env/bin/activate

pip install \
    babel \
    boto \
    fixtures \
    httplib2 \
    jsonschema \
    lxml \
    nose \
    nose-testconfig \
    paramiko \
    pyOpenSSL \
    python-keystoneclient \
    python-neutronclient \
    pyyaml \
    testresources \
    testtools
